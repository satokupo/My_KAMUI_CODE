#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compress_videos.py

このスクリプトは ffmpeg-python を利用して動画を圧縮するためのユーティリティです。
- 単一ファイルまたはディレクトリを入力として指定できます。
- 出力は同じ場所に *_compressed.mp4 を作成するか、--output-dir で別ディレクトリを指定可能です。
- 既定設定は H.264 + CRF=23 + preset=medium + 音声copy。
- CRF値やコーデック（h264/hevc/av1）、音声処理、faststart などをオプションで制御可能です。
- 元ファイルよりサイズが大きくなる場合はスキップし、--force-replace を付けると上書きします。

注意事項:
- このスクリプトは Windows 環境（Git Bash, PowerShell 等）での利用を想定しています。
- 出力メッセージは日本語を含みます。Python 3 は標準で UTF-8 を使用しますが、
  従来の Windows コマンドプロンプトでは文字化けする可能性があります。
  その場合は以下のいずれかを推奨します:
    * Git Bash / Windows Terminal を利用する
    * 環境変数 `PYTHONUTF8=1` を設定する
    * スクリプト内で `sys.stdout.reconfigure(encoding="utf-8")` を有効化する
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import argparse
import os
from pathlib import Path
import ffmpeg
import tempfile
import shutil
import time


VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}

CODEC_MAP = {
    "h264": "libx264",
    "hevc": "libx265",
    "av1":  "libaom-av1",  # CPUエンコード（遅いが高圧縮）
}

def human(n):
    for u in ["B","KB","MB","GB","TB"]:
        if n < 1024 or u == "TB":
            return f"{n:.1f}{u}"
        n /= 1024

def compress_one(
    in_path: Path,
    out_path: Path,
    vcodec: str,
    crf: int,
    preset: str,
    tune: str|None,
    audio_copy: bool,
    audio_bitrate: str|None,
    pix_fmt: str|None,
    faststart: bool,
) -> None:
    """1ファイルを圧縮。失敗時は例外送出。"""
    stream_in = ffmpeg.input(str(in_path))

    out_kwargs = {
        "vcodec": vcodec,
        "crf": crf,
        "preset": preset,
        # 映像のみ再エンコード、音声はオプションでcopy/再エンコード
        "movflags": "use_metadata_tags",
        "map_metadata": "0",
    }
    if tune:
        out_kwargs["tune"] = tune
    if pix_fmt:
        out_kwargs["pix_fmt"] = pix_fmt
    # mp4のシーク改善
    if faststart:
        out_kwargs["movflags"] = (out_kwargs.get("movflags","") + "+faststart").lstrip("+")

    if audio_copy:
        out_kwargs["acodec"] = "copy"
    else:
        out_kwargs["acodec"] = "aac"
        if audio_bitrate:
            out_kwargs["b:a"] = audio_bitrate

    # 容赦なく上書き
    out_kwargs["y"] = None

    (
        ffmpeg
        .output(stream_in, str(out_path), **out_kwargs)
        .global_args("-hide_banner", "-loglevel", "error")
        .run()
    )

def is_video_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in VIDEO_EXTS

def plan_output_path(in_file: Path, out_dir: Path|None) -> Path:
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / in_file.with_suffix(".mp4").name
    else:
        # 同じ場所に _compressed サフィックス
        return in_file.with_stem(in_file.stem + "_compressed").with_suffix(".mp4")

def main():
    parser = argparse.ArgumentParser(
        description="Loss-minimized video compression via ffmpeg-python."
    )
    parser.add_argument("input", help="入力ファイルまたはディレクトリのパス")
    parser.add_argument("-o", "--output-dir", help="出力先ディレクトリ（未指定なら同階層に *_compressed.mp4）")
    parser.add_argument("--codec", choices=["h264","hevc","av1"], default="h264", help="映像コーデック（既定: h264）")
    parser.add_argument("--crf", type=int, default=23, help="CRF（小さいほど高画質/大容量, 目安: 18〜28）")
    parser.add_argument("--preset", default="medium",
                        choices=["ultrafast","superfast","veryfast","faster","fast","medium","slow","slower","veryslow"],
                        help="圧縮速度/効率（既定: medium）")
    parser.add_argument("--tune", default=None, help="ffmpegのtune(e.g. film, animation, grain)")
    parser.add_argument("--audio-copy", action="store_true", default=True, help="音声を再エンコードせずcopy（既定）")
    parser.add_argument("--audio-reencode", dest="audio_copy", action="store_false", help="音声をAACで再エンコード")
    parser.add_argument("--audio-bitrate", default="192k", help="音声再エンコード時のビットレート（既定: 192k）")
    parser.add_argument("--pix-fmt", default=None, help="ピクセルフォーマット（例: yuv420p）")
    parser.add_argument("--faststart", action="store_true", help="mp4のfaststartを有効（Web配信用に先頭へmoov移動）")
    parser.add_argument("--force-replace", action="store_true", help="圧縮後が大きくても置換する（既定はサイズ悪化なら保留）")
    parser.add_argument("--dry-run", action="store_true", help="実際には書き出さず、処理対象と出力パスのみ表示")

    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.output_dir).resolve() if args.output_dir else None
    vcodec = CODEC_MAP[args.codec]

    targets: list[Path] = []
    if in_path.is_dir():
        for p in sorted(in_path.rglob("*")):
            if is_video_file(p):
                targets.append(p)
    elif is_video_file(in_path):
        targets.append(in_path)
    else:
        print("入力が動画ファイル/ディレクトリではありません。", file=sys.stderr)
        sys.exit(2)

    if not targets:
        print("処理対象となる動画が見つかりませんでした。", file=sys.stderr)
        sys.exit(3)

    print(f"[INFO] 対象 {len(targets)} 件 / codec={args.codec}, crf={args.crf}, preset={args.preset}, audio_copy={args.audio_copy}")

    total_saved = 0
    processed = 0
    for src in targets:
        dst = plan_output_path(src, out_dir)
        if args.dry_run:
            print(f"DRY-RUN: {src} -> {dst}")
            continue

        tmp_dir = Path(tempfile.mkdtemp(prefix="ffx_"))
        tmp_out = tmp_dir / (dst.name + ".tmp.mp4")

        try:
            t0 = time.time()
            compress_one(
                src, tmp_out, vcodec, args.crf, args.preset, args.tune,
                args.audio_copy, args.audio_bitrate, args.pix_fmt, args.faststart
            )
            enc_ms = (time.time() - t0) * 1000

            src_sz = src.stat().st_size
            out_sz = tmp_out.stat().st_size

            # サイズ悪化時のガード
            if (not args.force_retail := args.force_replace) and out_sz >= src_sz:
                print(f"[SKIP] 大きくなったため保留: {src.name} (src={human(src_sz)}, out={human(out_sz)})")
                continue

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(tmp_out), str(dst))
            saved = src_sz - out_sz
            total_saved += max(0, saved)
            processed += 1
            print(f"[OK] {src.name} -> {dst.name}  {human(src_sz)} -> {human(out_sz)}  (saved {human(max(0,saved))}, {enc_ms:.0f} ms)")
        except ffmpeg.Error as e:
            print(f"[ERR] {src.name}: {e.stderr.decode('ut
