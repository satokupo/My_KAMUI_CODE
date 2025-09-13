#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remove_bg.py

rembg を利用して画像の背景を透過（アルファ）にするユーティリティです。
- 単一ファイルまたはディレクトリを入力に指定可能（ディレクトリは再帰的に処理）
- 出力は PNG（透過対応）。既定では入力と同じ場所に *_nobg.png を作成
- --output-dir で一括出力先を指定可能
- モデル指定（--model）や、画質優先のアルファマッティング（--alpha-matting）有効化に対応
- 既に出力が存在する場合はスキップ（--force で上書き）

注意:
- Windows（Git Bash / PowerShell）での利用を想定。出力メッセージは日本語。
- 文字化けする場合は以下を推奨:
    * Git Bash / Windows Terminal を利用
    * 環境変数 PYTHONUTF8=1 を設定
    * 本スクリプトの stdout エンコーディングを UTF-8 に再設定（既に実装済み）
"""

import sys
# 日本語出力の文字化け対策（Python 3.7+）
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
from pathlib import Path
import shutil
import tempfile

from rembg import remove, new_session

# 対応拡張子
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}


def is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS


def iter_images(root: Path):
    if root.is_file():
        if is_image(root):
            yield root
    else:
        for p in sorted(root.rglob("*")):
            if is_image(p):
                yield p


def plan_output_path(inp: Path, out_dir: Path | None) -> Path:
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / (inp.stem + "_nobg.png")
    return inp.with_stem(inp.stem + "_nobg").with_suffix(".png")


def process_one(src: Path, dst: Path, session, args) -> tuple[bool, str]:
    if dst.exists() and not args.force:
        return False, f"[SKIP] 既に存在: {dst}"

    with open(src, "rb") as f:
        data = f.read()

    out_bytes = remove(
        data,
        session=session,
        alpha_matting=args.alpha_matting,
        alpha_matting_foreground_threshold=args.am_foreground_thresh,
        alpha_matting_background_threshold=args.am_background_thresh,
        alpha_matting_erode_size=args.am_erode,
        only_mask=args.only_mask,
        bg=args.bg,
    )

    tmpdir = Path(tempfile.mkdtemp(prefix="rbg_"))
    try:
        tmp_out = tmpdir / (dst.name + ".part")
        with open(tmp_out, "wb") as o:
            o.write(out_bytes)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_out), str(dst))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return True, f"[OK] {src.name} -> {dst.name}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="背景透過(Alpha)バッチ処理ツール（rembgベース）"
    )
    parser.add_argument("input", help="入力画像 or ディレクトリのパス")
    parser.add_argument("-o", "--output-dir", help="出力先ディレクトリ（未指定なら同階層に *_nobg.png）")
    parser.add_argument("--model", default=None,
                        help="使用モデル（例: u2net, u2netp, u2net_human_seg, isnet-general-use など。未指定は既定）")
    parser.add_argument("--alpha-matting", action="store_true",
                        help="画質優先のアルファマッティングを有効化（エッジを滑らかに）")
    parser.add_argument("--am-foreground-thresh", type=int, default=240,
                        help="アルファマッティング前景しきい値（既定: 240）")
    parser.add_argument("--am-background-thresh", type=int, default=10,
                        help="アルファマッティング背景しきい値（既定: 10）")
    parser.add_argument("--am-erode", type=int, default=10,
                        help="アルファマッティングの収縮サイズ（既定: 10）")
    parser.add_argument("--only-mask", action="store_true",
                        help="マスク画像のみを出力（デバッグ/特殊用途）")
    parser.add_argument("--bg", default=None,
                        help="透明ではなく単色背景で出力したい場合のRGBA色（例: #ffffffff ＝ 白不透明）")
    parser.add_argument("--force", action="store_true",
                        help="出力が既に存在しても上書き")
    parser.add_argument("--dry-run", action="store_true",
                        help="実際には処理せず、対象と出力先だけ表示")

    args = parser.parse_args()
    inp = Path(args.input)
    out_dir = Path(args.output_dir).resolve() if args.output_dir else None

    if not inp.exists():
        print(f"[ERR] 入力が存在しません: {inp}", file=sys.stderr)
        return 2

    try:
        session = new_session(args.model) if args.model else new_session()
    except Exception as e:
        print("[ERR] モデル初期化に失敗しました:", e, file=sys.stderr)
        return 3

    targets = list(iter_images(inp))
    if not targets:
        print("[WARN] 対象画像が見つかりませんでした。対応拡張子:",
              ", ".join(sorted(IMAGE_EXTS)))
        return 0

    print(f"[INFO] 対象 {len(targets)} 件 / model={args.model or 'default'}"
          f" / alpha_matting={args.alpha_matting}")

    done = 0
    for src in targets:
        dst = plan_output_path(src, out_dir)
        if args.dry_run:
            print(f"DRY-RUN: {src} -> {dst}")
            continue

        ok, msg = process_one(src, dst, session, args)
        print(msg)
        if ok:
            done += 1

    print(f"[DONE] {done}/{len(targets)} 件 完了")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
