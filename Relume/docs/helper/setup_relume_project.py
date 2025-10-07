#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relumeプロジェクトセットアップスクリプト

目的:
  RelumeからダウンロードしたワイヤーフレームHTMLを、
  デザインブラッシュアップ可能な状態に自動セットアップする

使用方法:
  python setup_relume_project.py <ターゲットディレクトリパス>
  例: python setup_relume_project.py "s:/MyProjects/KAMUI_CODE/Relume/2025-10-07_satokupo-design/01_ホーム"

処理フロー:
  1. 引数からターゲットディレクトリパスを受け取る
  2. ターゲットディレクトリ内のindex.htmlを読み込む
  3. HTML基本タグ（<!DOCTYPE>, <html>, <head>, <body>）でラップ
     - Tailwind CDN読み込み
     - assets/style/global.css読み込み
     - assets/js/script.js読み込み
     - titleはディレクトリ名から自動生成（"01_ホーム" → "ホーム"）
  4. 既存コンテンツの各セクション（<section>, <div>, <header>, <footer>等の主要要素）にユニークIDを自動付与
     - ID命名規則: section-{連番} (例: section-1, section-2, ...)
     - または意味のある名前を推測可能なら付与（例: header → section-header）
  5. 必要なディレクトリ構造を生成
     - assets/js/
     - assets/style/
     - assets/images/
     - screenshots/
     - temp/
     - docs/
  6. 空ファイルを生成
     - assets/style/global.css（CSSネストルール案内コメント付き）
     - assets/js/script.js（空ファイル）
  7. 修正されたHTMLを上書き保存
  8. 実行結果レポートをコンソールに出力
     - 生成されたディレクトリ一覧
     - 生成されたファイル一覧
     - 付与されたセクションID一覧

注意事項:
  - index.htmlが存在しない場合はエラー終了
  - すでにHTML基本タグが存在する場合はスキップ（冪等性確保）
  - 既存ディレクトリ・ファイルは上書きしない（存在チェック）

今後の拡張可能性:
  - 複数ページを一括処理するオプション（--all等）
  - セクションID命名規則のカスタマイズオプション
  - テンプレートのカスタマイズ（meta tagの追加等）
"""

import sys
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup


def print_info(message):
    """情報メッセージを出力"""
    print(f"[INFO] {message}")


def print_success(message):
    """成功メッセージを出力"""
    print(f"[SUCCESS] {message}")


def print_error(message):
    """エラーメッセージを出力"""
    print(f"[ERROR] {message}", file=sys.stderr)


def create_directory_structure(base_path):
    """
    必要なディレクトリ構造を作成

    Args:
        base_path: ベースとなるディレクトリパス

    Returns:
        作成されたディレクトリのリスト
    """
    directories = [
        "assets/js",
        "assets/style",
        "assets/images",
        "screenshots",
        "temp",
        "docs"
    ]

    created_dirs = []
    for dir_path in directories:
        full_path = base_path / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(full_path))
            print_info(f"ディレクトリ作成: {full_path}")
        else:
            print_info(f"ディレクトリ既存: {full_path}")

    return created_dirs


def create_empty_files(base_path):
    """
    空ファイルを作成

    Args:
        base_path: ベースとなるディレクトリパス

    Returns:
        作成されたファイルのリスト
    """
    # global.css用のコメント（CSSネストルール案内）
    css_comment = """/*
 * CSSネストルール遵守
 * - 各セクションは必ずセクションIDで開始し、すべてのスタイルをその中に記述
 * - 内容が他のセクションに漏れ出さないよう、必ずネスト構造を維持する
 *
 * 例:
 * #section-hero {
 *   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 *
 *   .hero-title {
 *     font-size: 3rem;
 *     font-weight: bold;
 *   }
 *
 *   .hero-button {
 *     background: white;
 *     color: #667eea;
 *   }
 * }
 */

"""

    files = {
        "assets/style/global.css": css_comment,
        "assets/js/script.js": ""
    }

    created_files = []
    for file_path, content in files.items():
        full_path = base_path / file_path
        if not full_path.exists():
            full_path.write_text(content, encoding="utf-8")
            created_files.append(str(full_path))
            print_info(f"ファイル作成: {full_path}")
        else:
            print_info(f"ファイル既存: {full_path}")

    return created_files


def extract_page_title(dir_name):
    """
    ディレクトリ名からページタイトルを抽出

    Args:
        dir_name: ディレクトリ名（例: "01_ホーム"）

    Returns:
        タイトル（例: "ホーム"）
    """
    # 連番を除去（01_, 02_など）
    title = re.sub(r'^\d+_', '', dir_name)
    return title


def ask_section_name(section_index, section_element):
    """
    ユーザーにセクション名を質問

    Args:
        section_index: セクションのインデックス
        section_element: セクションのBeautifulSoup要素

    Returns:
        セクション名
    """
    # セクション内のテキストを取得（最初の50文字）
    text_content = section_element.get_text(strip=True)[:50]

    print(f"\n--- セクション {section_index + 1} ---")
    print(f"内容: {text_content}...")

    # ユーザーに入力を求める
    section_name = input(f"このセクションの名前を入力してください（例: hero, features, contact）: ").strip()

    # 入力が空の場合はデフォルト名
    if not section_name:
        section_name = f"section-{section_index + 1}"
    else:
        # セクション名をID形式に整形（英数字とハイフンのみ）
        section_name = re.sub(r'[^a-zA-Z0-9-]', '', section_name.lower())
        section_name = f"section-{section_name}"

    return section_name


def add_section_ids(soup):
    """
    セクションにユニークIDを付与（ユーザー対話型）

    Args:
        soup: BeautifulSoupオブジェクト

    Returns:
        付与されたID一覧
    """
    # 主要なセクション要素を検出
    section_tags = ['section', 'header', 'footer', 'main', 'nav', 'aside']
    sections = soup.find_all(section_tags)

    assigned_ids = []

    print_info(f"{len(sections)}個のセクションを検出しました")
    print("\n各セクションに意味のあるIDを付与します。")

    for index, section in enumerate(sections):
        # 既にIDが付与されている場合はスキップ
        if section.get('id'):
            print_info(f"セクション {index + 1} は既にID '{section['id']}' を持っています")
            assigned_ids.append(section['id'])
            continue

        # ユーザーにセクション名を質問
        section_id = ask_section_name(index, section)

        # IDを付与
        section['id'] = section_id
        assigned_ids.append(section_id)
        print_success(f"ID '{section_id}' を付与しました")

    return assigned_ids


def wrap_with_html_template(content, title, base_path):
    """
    コンテンツをHTML基本タグでラップ

    Args:
        content: 既存のHTMLコンテンツ
        title: ページタイトル
        base_path: ベースとなるディレクトリパス

    Returns:
        ラップされたHTML文字列
    """
    template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="assets/style/global.css">
</head>
<body>
{content}
<script src="assets/js/script.js"></script>
</body>
</html>"""

    return template


def check_if_already_wrapped(html_content):
    """
    HTMLが既に基本タグでラップされているかチェック

    Args:
        html_content: HTMLコンテンツ

    Returns:
        True: 既にラップ済み, False: 未ラップ
    """
    return html_content.strip().startswith('<!DOCTYPE html>')


def process_page(page_path):
    """
    ページディレクトリを処理

    Args:
        page_path: ページディレクトリのパス
    """
    page_path = Path(page_path)
    html_path = page_path / "index.html"

    # index.htmlの存在チェック
    if not html_path.exists():
        print_error(f"index.htmlが見つかりません: {html_path}")
        return False

    print_info(f"処理開始: {page_path}")

    # ディレクトリ構造を作成
    created_dirs = create_directory_structure(page_path)

    # 空ファイルを作成
    created_files = create_empty_files(page_path)

    # HTMLファイルを読み込み
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 既にラップされているかチェック
    if check_if_already_wrapped(html_content):
        print_info("HTML基本タグは既に存在しています。セクションID付与のみ実行します。")

        # セクションID付与
        soup = BeautifulSoup(html_content, 'html.parser')
        assigned_ids = add_section_ids(soup)

        # HTMLを保存
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

        print_success(f"セクションID付与完了: {len(assigned_ids)}個のIDを付与")
        return True

    # BeautifulSoupでパース
    soup = BeautifulSoup(html_content, 'html.parser')

    # セクションにIDを付与
    assigned_ids = add_section_ids(soup)

    # ページタイトルを生成
    title = extract_page_title(page_path.name)

    # HTML基本タグでラップ
    wrapped_html = wrap_with_html_template(str(soup), title, page_path)

    # HTMLファイルを上書き保存
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(wrapped_html)

    # レポート出力
    print_success(f"\n=== 処理完了: {page_path.name} ===")
    print(f"生成ディレクトリ数: {len(created_dirs)}")
    print(f"生成ファイル数: {len(created_files)}")
    print(f"付与セクションID数: {len(assigned_ids)}")
    print(f"付与されたID: {', '.join(assigned_ids)}")

    return True


def main():
    """メイン処理"""
    # コマンドライン引数をチェック
    if len(sys.argv) < 2:
        print_error("使用方法: python setup_relume_project.py <ターゲットディレクトリパス>")
        sys.exit(1)

    target_path = sys.argv[1]

    # パスの存在チェック
    if not os.path.exists(target_path):
        print_error(f"指定されたパスが存在しません: {target_path}")
        sys.exit(1)

    # 処理実行
    success = process_page(target_path)

    if success:
        print_success("\n全ての処理が正常に完了しました!")
        sys.exit(0)
    else:
        print_error("\n処理中にエラーが発生しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
