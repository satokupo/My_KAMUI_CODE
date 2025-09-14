#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image_converter.py

このスクリプトは Pillow + pillow-heif を利用して画像を別形式に変換するユーティリティです。
- 単一ファイルまたはディレクトリを入力として指定できます。
- 出力は同じ場所に *_converted.{拡張子} を作成するか、--output-dir で別ディレクトリを指定可能です。
- デフォルトは JPEG 形式で保存します。
- HEIC/HEIF に対応するため pillow-heif を利用しています。
- PNG/WebP などアルファチャンネルを持つ形式を JPEG に変換する場合は、背景色で合成します。

注意事項:
- このスクリプトは Windows 環境（Git Bash, PowerShell 等）でも利用可能です。
- 出力メッセージは日本語を含みます。文字化けする場合は以下を推奨:
    * Git Bash / Windows Terminal を利用する
    * 環境変数 `PYTHONUTF8=1` を設定する
    * sys.stdout.reconfigure(encoding="utf-8") を有効化する
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import argparse
from pathlib import Path
from PIL import Image, ImageOps
import pillow_heif   # HEIC/HEIF対応のためインポートするだけで有効になる

# HEIC/HEIF対応を明示的に有効化
pillow_heif.register_heif_opener()

# 対応画像拡張子
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic", ".heif"}

def is_image_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS

def plan_output_path(in_file: Path, out_dir: Path|None, fmt: str) -> Path:
    """出力パスを決定"""
    ext = "." + fmt.lower().replace("jpeg", "jpg")
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / (in_file.stem + "_converted" + ext)
    else:
        return in_file.with_stem(in_file.stem + "_converted").with_suffix(ext)

def convert_one(
    in_path: Path,
    out_path: Path,
    fmt: str,
    quality: int,
    background: tuple[int,int,int],
    keep_exif: bool,
    optimize: bool,
    progressive: bool,
) -> None:
    """1ファイルを変換。失敗時は例外送出。"""
    with Image.open(in_path) as im:
        # EXIFの回転情報を適用
        im = ImageOps.exif_transpose(im)

        # 透過をJPEGへ変換する場合は背景合成
        if fmt.upper() == "JPEG" and im.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", im.size, background)
            bg.paste(im, mask=im.split()[-1])
            im = bg
        elif fmt.upper() == "JPEG" and im.mode not in ("RGB", "L"):
            im = im.convert("RGB")

        save_kwargs = {}
        if fmt.upper() == "JPEG":
            save_kwargs.update(dict(quality=quality, optimize=optimize, progressive=progressive))

        # EXIFとICCを保持（必要に応じて）
        exif = im.info.get("exif")
        icc = im.info.get("icc_profile")
        if keep_exif and exif:
            save_kwargs["exif"] = exif
        if icc:
            save_kwargs["icc_profile"] = icc

        im.save(out_path, fmt.upper(), **save_kwargs)

def main():
    parser = argparse.ArgumentParser(
        description="汎用画像フォーマット変換 (Pillow + pillow-heif)"
    )
    parser.add_argument("input", help="入力ファイルまたはディレクトリのパス")
    parser.add_argument("-o", "--output-dir", help="出力先ディレクトリ")
    parser.add_argument("--to", default="JPEG", help="出力フォーマット（JPEG/PNG/WebP/TIFF 等）")
    parser.add_argument("--quality", type=int, default=95, help="JPEG保存時の品質 (1〜100)")
    parser.add_argument("--bg", nargs=3, type=int, metavar=("R","G","B"),
                        default=(255,255,255), help="透過をJPEGに変換する際の背景色 (既定: 白)")
    parser.add_argument("--no-exif", action="store_true", help="EXIFを保存しない")
    parser.add_argument("--no-optimize", action="store_true", help="JPEG最適化を無効化")
    parser.add_argument("--no-progressive", action="store_true", help="プログレッシブJPEGを無効化")
    parser.add_argument("--dry-run", action="store_true", help="実際には保存せず対象のみ表示")

    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.output_dir).resolve() if args.output_dir else None

    targets: list[Path] = []
    if in_path.is_dir():
        for p in sorted(in_path.rglob("*")):
            if is_image_file(p):
                targets.append(p)
    elif is_image_file(in_path):
        targets.append(in_path)
    else:
        print("入力が画像ファイル/ディレクトリではありません。", file=sys.stderr)
        sys.exit(2)

    if not targets:
        print("処理対象となる画像が見つかりませんでした。", file=sys.stderr)
        sys.exit(3)

    print(f"[INFO] 対象 {len(targets)} 件 / 出力形式={args.to}")

    processed = 0
    for src in targets:
        dst = plan_output_path(src, out_dir, args.to)
        if args.dry_run:
            print(f"DRY-RUN: {src} -> {dst}")
            continue

        try:
            convert_one(
                src, dst, args.to, args.quality, tuple(args.bg),
                not args.no_exif, not args.no_optimize, not args.no_progressive
            )
            processed += 1
            print(f"[OK] {src.name} -> {dst.name}")
        except Exception as e:
            print(f"[ERR] {src.name}: {e}")

    print(f"\n[完了] {processed} ファイル変換しました。")

if __name__ == "__main__":
    main()
