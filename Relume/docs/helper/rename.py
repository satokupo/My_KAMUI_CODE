#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用リネームヘルパー

使い方:
  python _workbench/helper/rename.py --path <対象のフルパス> --new-name <新しい名前>

特徴:
- 破壊的操作はデフォルトで行いません（同名が存在する場合は失敗）。--overwrite 指定で上書き可能。
- --dry-run で実際の変更を行わず計画のみ表示。
- Windows の大文字小文字だけを変更するリネームを 2 段階で安全に実行。
- ファイル/ディレクトリの両方に対応。移動は行わず、親ディレクトリ内での名称変更のみを行います。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import io
import os as _os
from pathlib import Path


def is_case_only_change(old_name: str, new_name: str) -> bool:
    return old_name.lower() == new_name.lower() and old_name != new_name


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def validate_new_name(name: str) -> None:
    if not name or name in {".", ".."}:
        raise ValueError("新しい名前が不正です")
    # パス区切りを含めない（移動はサポート外）。必要なら今後 --dest を追加。
    if any(sep in name for sep in ("/", "\\")):
        raise ValueError("新しい名前にパス区切りは使用できません（同一ディレクトリ内の改名のみ）")


def plan_rename(src: Path, new_name: str) -> Path:
    parent = src.parent
    return parent / new_name


def perform_rename(src: Path, dst: Path, overwrite: bool, verbose: bool) -> None:
    if dst.exists():
        if not overwrite:
            raise FileExistsError(f"すでに存在します: {dst}")
        if verbose:
            print(f"[INFO] --overwrite 指定により既存を削除します: {dst}")
        remove_path(dst)

    # Windows での大文字小文字変更のみ対策（2段階リネーム）
    if is_case_only_change(src.name, dst.name):
        tmp = src.with_name(src.name + ".tmp-rename")
        # 念のため tmp が存在していれば除去
        if tmp.exists():
            remove_path(tmp)
        if verbose:
            print(f"[INFO] case-only rename: {src.name} -> {dst.name} (via {tmp.name})")
        src.rename(tmp)
        tmp.rename(dst)
        return

    src.rename(dst)


def main() -> int:
    # 標準入出力/エラーをUTF-8に固定
    try:
        if getattr(sys.stdout, "reconfigure", None):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        if getattr(sys.stderr, "reconfigure", None):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        if getattr(sys.stdin, "reconfigure", None):
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass
    _os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    ap = argparse.ArgumentParser(description="Generic file/dir renamer")
    # 単体リネーム用（従来機能）
    ap.add_argument("--path", required=False, help="対象のフルパス（ファイル/ディレクトリ）")
    ap.add_argument("--new-name", required=False, help="新しい名前（同一ディレクトリ内）")
    # 共通オプション
    ap.add_argument("--dry-run", action="store_true", help="変更を実行せず計画のみ表示")
    ap.add_argument("--overwrite", action="store_true", help="宛先が存在する場合に削除してから上書き")
    ap.add_argument("--verbose", action="store_true", help="詳細ログ出力")
    # 拡張: 一覧/バッチ
    ap.add_argument("--root-dir", help="親ディレクトリ（一覧/バッチ用）")
    ap.add_argument("--list-children", action="store_true", help="root-dir 直下のディレクトリ名を一覧出力")
    ap.add_argument(
        "--mapping",
        help=(
            "旧名→新名の JSON 文字列（例: '{\"ホーム\":\"01-home\",\"料金\":\"04-pricing\"}')。"
            "--root-dir と併用し、バッチで順次リネームを実行。"
        ),
    )
    args = ap.parse_args()

    # モード判定: 一覧
    if args.list_children:
        if not args.root_dir:
            print("[ERROR] --list-children は --root-dir と併用してください", file=sys.stderr)
            return 1
        root = Path(args.root_dir)
        if not root.exists() or not root.is_dir():
            print(f"[ERROR] root-dir が見つかりません: {root}", file=sys.stderr)
            return 1
        for p in sorted(root.iterdir()):
            if p.is_dir():
                print(p.name)
        return 0

    # モード判定: バッチ（JSON マッピング）
    if args.mapping:
        if not args.root_dir:
            print("[ERROR] --mapping は --root-dir と併用してください", file=sys.stderr)
            return 1
        root = Path(args.root_dir)
        if not root.exists() or not root.is_dir():
            print(f"[ERROR] root-dir が見つかりません: {root}", file=sys.stderr)
            return 1
        try:
            mapping = json.loads(args.mapping)
            if not isinstance(mapping, dict):
                raise ValueError("mapping は JSON オブジェクトである必要があります")
        except Exception as e:
            print(f"[ERROR] mapping の解析に失敗しました: {e}", file=sys.stderr)
            return 1

        # 事前検証
        new_names = set()
        for old_name, new_name in mapping.items():
            try:
                validate_new_name(new_name)
            except Exception as e:
                print(f"[ERROR] 新名が不正です ({old_name} -> {new_name}): {e}", file=sys.stderr)
                return 1
            if new_name in new_names:
                print(f"[ERROR] 新名が重複しています: {new_name}", file=sys.stderr)
                return 1
            new_names.add(new_name)

        # 存在/衝突チェックと計画表示
        plans: list[tuple[Path, Path]] = []
        for old_name, new_name in mapping.items():
            src = root / old_name
            if not src.exists():
                print(f"[ERROR] 対象が見つかりません: {src}", file=sys.stderr)
                return 1
            dst = plan_rename(src, new_name)
            if args.verbose:
                print(f"[PLAN] {src} -> {dst}")
            if dst.exists() and not args.overwrite:
                print(f"[ERROR] すでに存在します（--overwrite なし）: {dst}", file=sys.stderr)
                return 1
            plans.append((src, dst))

        if args.dry_run:
            print("--dry-run: バッチ実行しませんでした")
            return 0

        # 実行
        for src, dst in plans:
            try:
                perform_rename(src, dst, overwrite=args.overwrite, verbose=args.verbose)
                print(f"✅ renamed: {src} -> {dst}")
            except Exception as e:
                print(f"[ERROR] リネームに失敗しました: {src} -> {dst}: {e}", file=sys.stderr)
                return 1
        return 0

    # 単体リネーム（従来モード）
    if not args.path or not args.new_name:
        print("[ERROR] 単体リネームは --path と --new-name が必要です（または --list-children / --mapping を使用）", file=sys.stderr)
        return 1

    src = Path(args.path)
    try:
        validate_new_name(args.new_name)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    if not src.exists():
        print(f"[ERROR] 対象が見つかりません: {src}", file=sys.stderr)
        return 1

    dst = plan_rename(src, args.new_name)

    if args.verbose:
        print(f"[PLAN] {src} -> {dst}")

    if args.dry_run:
        print("--dry-run: 実行しませんでした")
        return 0

    try:
        perform_rename(src, dst, overwrite=args.overwrite, verbose=args.verbose)
    except Exception as e:
        print(f"[ERROR] リネームに失敗しました: {e}", file=sys.stderr)
        return 1

    print(f"✅ renamed: {src} -> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


