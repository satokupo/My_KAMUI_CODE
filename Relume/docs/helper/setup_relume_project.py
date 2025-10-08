#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relumeプロジェクトセットアップスクリプト

目的:
  RelumeからダウンロードしたワイヤーフレームHTMLを、
  デザインブラッシュアップ可能な状態に自動セットアップする

使用方法:
  # 単一ページ処理
  python setup_relume_project.py --page-dir "<ページディレクトリパス>" --sections "nav,hero,features,footer"

  # 複数ページ一括処理
  python setup_relume_project.py \
    --root-dir "<ルートディレクトリ>" \
    --page "ホーム:nav,hero,features,footer" \
    --page "料金:nav,pricing,faq,footer"

処理フロー:
  1. 引数からセクション構成情報を受け取る
  2. setup_templates/ディレクトリ構造を丸ごとコピー
  3. ターゲットディレクトリ内のindex.htmlを読み込む
  4. HTML基本タグ（<!DOCTYPE>, <html>, <head>, <body>）でラップ
     - Tailwind CDN読み込み
     - assets/style/base.css, custom.css読み込み
     - assets/js/main.js読み込み
  5. 文書内で最初に現れる<section>を<header>でラップ
  6. 引数で指定されたセクション名を順番に適用（セクション数検証あり）
  7. 修正されたHTMLを上書き保存
  8. 実行結果レポートをコンソールに出力

注意事項:
  - index.htmlが存在しない場合はエラー終了
  - セクション数が一致しない場合はエラー表示して中断
  - 既存ディレクトリ・ファイルは上書きしない（存在チェック）
"""

import sys
import os
import io
import re
import shutil
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

# Windows環境での文字コード問題を解決
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def print_info(message):
    """情報メッセージを出力"""
    print(f"[INFO] {message}")


def print_success(message):
    """成功メッセージを出力"""
    print(f"[SUCCESS] {message}")


def print_error(message):
    """エラーメッセージを出力"""
    print(f"[ERROR] {message}", file=sys.stderr)


def copy_template_structure(template_path, target_path):
    """
    テンプレートディレクトリ構造を対象ディレクトリにコピー

    Args:
        template_path: テンプレートディレクトリのパス
        target_path: コピー先のディレクトリパス

    Returns:
        コピーされたファイル・ディレクトリのリスト
    """
    copied_items = []

    if not template_path.exists():
        print_error(f"テンプレートディレクトリが見つかりません: {template_path}")
        return copied_items

    # テンプレート内のすべてのファイル・ディレクトリを走査
    for item in template_path.rglob('*'):
        # 相対パスを計算
        relative_path = item.relative_to(template_path)
        target_item = target_path / relative_path

        # ディレクトリの場合
        if item.is_dir():
            if not target_item.exists():
                target_item.mkdir(parents=True, exist_ok=True)
                copied_items.append(f"[DIR] {target_item}")
                print_info(f"ディレクトリ作成: {target_item}")
            else:
                print_info(f"ディレクトリ既存: {target_item}")
        # ファイルの場合
        else:
            if not target_item.exists():
                shutil.copy2(item, target_item)
                copied_items.append(f"[FILE] {target_item}")
                print_info(f"ファイルコピー: {target_item}")
            else:
                print_info(f"ファイル既存: {target_item}")

    return copied_items


def extract_page_title(dir_name):
    """
    ディレクトリ名からページタイトルを抽出

    Args:
        dir_name: ディレクトリ名（例: "01_ホーム", "ホーム"）

    Returns:
        タイトル（例: "ホーム"）
    """
    # 連番を除去（01_, 02_など）
    title = re.sub(r'^\d+_', '', dir_name)
    return title


def get_section_preview(section_element):
    """
    セクションの概要を取得（デバッグ用）

    Args:
        section_element: セクションのBeautifulSoup要素

    Returns:
        セクション概要文字列
    """
    tag_name = section_element.name
    classes = ' '.join(section_element.get('class', []))
    text_preview = section_element.get_text(strip=True)[:60]

    return f"<{tag_name} class=\"{classes}\"> {text_preview}..."


def validate_section_count(sections, section_names, page_name):
    """
    セクション数を検証

    Args:
        sections: HTML内のセクション要素リスト
        section_names: ユーザー指定のセクション名リスト
        page_name: ページ名

    Returns:
        True: 一致, False: 不一致
    """
    actual_count = len(sections)
    expected_count = len(section_names)

    if actual_count == expected_count:
        return True

    # エラーメッセージを表示
    print_error(f"\n⚠️  [{page_name}] セクション数が一致しません")
    print(f"\n  【引数で指定】: {expected_count}個")
    print(f"    {', '.join(section_names)}")
    print(f"\n  【HTML内の実際】: {actual_count}個\n")

    # 各セクションの概要を表示
    print("  各セクションの概要:")
    for i, section in enumerate(sections):
        preview = get_section_preview(section)
        print(f"    [{i+1}] {preview}")

    print("\n  考えられる原因:")
    print("    - ビジュアル的に1つに見えるが、コード上は2つのセクションに分かれている")
    print("    - または、ビジュアル的に2つに見えるが、コード上は1つのセクションになっている")
    print("\n  上記を確認の上、正しいセクション名リストを指定してください。\n")

    return False


def wrap_first_section_with_header(soup):
    """
    文書内で最初に現れる<section>を<header>でラップ

    Args:
        soup: BeautifulSoupオブジェクト

    Returns:
        処理が実行されたかどうか（True: 実行, False: スキップ）
    """
    # 最初の<section>を検索
    first_section = soup.find('section')

    # <section>が存在しない場合はスキップ
    if not first_section:
        print_info("文書内に<section>が見つかりませんでした。header ラップ処理をスキップします。")
        return False

    # 既に<header>の子要素になっている場合はスキップ
    if first_section.parent and first_section.parent.name == 'header':
        print_info("最初の<section>は既に<header>でラップされています。")
        return False

    # 新しい<header>要素を作成
    new_header = soup.new_tag('header')

    # 最初の<section>を<header>で置換
    first_section.wrap(new_header)

    print_success("最初の<section>を<header>でラップしました。")
    return True


def add_section_ids(soup, section_names, page_name, count_wrapped_header=False):
    """
    セクションにユニークIDを付与（引数ベース）

    Args:
        soup: BeautifulSoupオブジェクト
        section_names: セクション名リスト
        page_name: ページ名（エラー表示用）
        count_wrapped_header: ラップされた<header>をカウントに含めるか（デフォルト: False）

    Returns:
        付与されたID一覧（成功時）、Noneまたは空リスト（失敗時）
    """
    # 主要なセクション要素を検出
    section_tags = ['section', 'header', 'footer', 'main', 'nav', 'aside']
    sections = soup.find_all(section_tags)

    # セクション数の検証
    if not validate_section_count(sections, section_names, page_name):
        return None

    assigned_ids = []

    print_info(f"{len(sections)}個のセクションを検出しました")

    for index, section in enumerate(sections):
        section_id = section_names[index]

        # 既にIDが付与されている場合は上書き
        if section.get('id'):
            print_info(f"セクション {index + 1} の既存ID '{section['id']}' を '{section_id}' に更新")

        # IDを付与
        section['id'] = section_id
        assigned_ids.append(section_id)
        print_success(f"ID '{section_id}' を付与しました")

    return assigned_ids


def wrap_with_html_template(content, title):
    """
    コンテンツをHTML基本タグでラップ

    Args:
        content: 既存のHTMLコンテンツ
        title: ページタイトル

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
  <link rel="stylesheet" href="assets/style/base.css">
  <link rel="stylesheet" href="assets/style/custom.css">
</head>
<body>
<div id="content-area">
{content}
</div>
<script type="module" src="assets/js/main.js"></script>
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


def process_page(page_path, template_path, section_names):
    """
    ページディレクトリを処理

    Args:
        page_path: ページディレクトリのパス
        template_path: テンプレートディレクトリのパス
        section_names: セクション名リスト

    Returns:
        True: 成功, False: 失敗
    """
    page_path = Path(page_path)
    html_path = page_path / "index.html"
    page_name = page_path.name

    # index.htmlの存在チェック
    if not html_path.exists():
        print_error(f"index.htmlが見つかりません: {html_path}")
        return False

    print_info(f"処理開始: {page_path}")

    # テンプレート構造をコピー
    copied_items = copy_template_structure(template_path, page_path)

    # HTMLファイルを読み込み
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 既にラップされているかチェック
    if check_if_already_wrapped(html_content):
        print_info("HTML基本タグは既に存在しています。header ラップとセクションID付与のみ実行します。")

        # BeautifulSoupでパース
        soup = BeautifulSoup(html_content, 'html.parser')

        # wrap前のセクション数を検証
        section_tags = ['section', 'footer', 'main', 'nav', 'aside']  # headerは除外
        sections_before_wrap = soup.find_all(section_tags)

        if not validate_section_count(sections_before_wrap, section_names, page_name):
            print_error(f"[{page_name}] セクション数不一致のため処理を中断しました")
            return False

        # 最初の<section>を<header>でラップ
        wrap_first_section_with_header(soup)

        # wrap後のセクションにIDを付与（headerは除外してsectionのみ）
        section_tags_for_id = ['section', 'footer', 'main', 'nav', 'aside']
        sections_for_id = soup.find_all(section_tags_for_id)

        assigned_ids = []
        print_info(f"{len(sections_for_id)}個のセクションにIDを付与します")

        for index, section in enumerate(sections_for_id):
            section_id = section_names[index]

            if section.get('id'):
                print_info(f"セクション {index + 1} の既存ID '{section['id']}' を '{section_id}' に更新")

            section['id'] = section_id
            assigned_ids.append(section_id)
            print_success(f"ID '{section_id}' を付与しました")

        # HTMLを保存
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

        print_success(f"処理完了: {len(assigned_ids)}個のIDを付与")
        return True

    # BeautifulSoupでパース
    soup = BeautifulSoup(html_content, 'html.parser')

    # wrap前のセクション数を検証
    section_tags = ['section', 'footer', 'main', 'nav', 'aside']  # headerは除外
    sections_before_wrap = soup.find_all(section_tags)

    if not validate_section_count(sections_before_wrap, section_names, page_name):
        print_error(f"[{page_name}] セクション数不一致のため処理を中断しました")
        return False

    # 最初の<section>を<header>でラップ
    wrap_first_section_with_header(soup)

    # wrap後のセクションにIDを付与（headerは除外してsectionのみ）
    section_tags_for_id = ['section', 'footer', 'main', 'nav', 'aside']
    sections_for_id = soup.find_all(section_tags_for_id)

    assigned_ids = []
    print_info(f"{len(sections_for_id)}個のセクションにIDを付与します")

    for index, section in enumerate(sections_for_id):
        section_id = section_names[index]

        if section.get('id'):
            print_info(f"セクション {index + 1} の既存ID '{section['id']}' を '{section_id}' に更新")

        section['id'] = section_id
        assigned_ids.append(section_id)
        print_success(f"ID '{section_id}' を付与しました")

    # ページタイトルを生成
    title = extract_page_title(page_path.name)

    # HTML基本タグでラップ
    wrapped_html = wrap_with_html_template(str(soup), title)

    # HTMLファイルを上書き保存（インデント整形）
    soup_final = BeautifulSoup(wrapped_html, 'html.parser')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(soup_final.prettify())

    # レポート出力
    print_success(f"\n=== 処理完了: {page_path.name} ===")
    print(f"コピーされた項目数: {len(copied_items)}")
    print(f"付与セクションID数: {len(assigned_ids)}")
    print(f"付与されたID: {', '.join(assigned_ids)}")

    return True


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='Relumeプロジェクトセットアップスクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 単一ページ処理
  python setup_relume_project.py --page-dir "path/to/ホーム" --sections "nav,hero,features,footer"

  # 複数ページ一括処理
  python setup_relume_project.py \\
    --root-dir "path/to/root" \\
    --page "ホーム:nav,hero,features,footer" \\
    --page "料金:nav,pricing,faq,footer"
        """
    )

    parser.add_argument('--page-dir', type=str, help='単一ページディレクトリのパス')
    parser.add_argument('--sections', type=str, help='セクション名（カンマ区切り）')
    parser.add_argument('--root-dir', type=str, help='複数ページ処理時のルートディレクトリ')
    parser.add_argument('--page', action='append', help='ページ設定（ページ名:section1,section2,...）')

    args = parser.parse_args()

    # テンプレートディレクトリのパスを取得
    script_dir = Path(__file__).parent
    template_path = script_dir / "setup_templates"

    # 単一ページ処理
    if args.page_dir and args.sections:
        section_list = [s.strip() for s in args.sections.split(',')]
        success = process_page(args.page_dir, template_path, section_list)

        if success:
            print_success("\n全ての処理が正常に完了しました!")
            sys.exit(0)
        else:
            print_error("\n処理中にエラーが発生しました")
            sys.exit(1)

    # 複数ページ一括処理
    elif args.root_dir and args.page:
        root_path = Path(args.root_dir)
        all_success = True

        for page_spec in args.page:
            if ':' not in page_spec:
                print_error(f"ページ設定の形式が不正です: {page_spec}")
                print_error("正しい形式: ページ名:section1,section2,...")
                sys.exit(1)

            page_name, sections = page_spec.split(':', 1)
            page_path = root_path / page_name
            section_list = [s.strip() for s in sections.split(',')]

            print(f"\n{'='*60}")
            print(f"ページ処理: {page_name}")
            print(f"{'='*60}\n")

            success = process_page(page_path, template_path, section_list)
            if not success:
                all_success = False

        if all_success:
            print_success("\n全ページの処理が正常に完了しました!")
            sys.exit(0)
        else:
            print_error("\n一部のページで処理エラーが発生しました")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
