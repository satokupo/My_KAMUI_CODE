# Tailwind CSS適用作業記録

## 作業日時
2025-10-06

## 作業内容

### 背景
- RelumeツールでホームページのワイヤーフレームをHTML出力
- 出力されたHTMLはTailwind CSS前提で構築されていたが、HTML構造が不完全だった
- 各ページが別々のフォルダ内の`index.html`として保存されている

### 問題点
- 出力されたHTMLには`<html>`, `<head>`, `<body>`タグが欠けていた
- CSSフレームワーク(Tailwind CSS)が読み込まれていなかった
- そのままではブラウザで正しく表示できない状態

### 実施した対応

#### 対応方針の決定
当初、以下の選択肢を検討:
1. **ラッパーHTML方式**: 1つのHTMLで各コンテンツを動的読み込み
   - 問題: ローカル環境でCORSエラーが発生する
   - 問題: 簡易サーバーが必要になる

2. **直接埋め込み方式**: 各HTMLファイルに直接HTML構造を追加 ✅採用
   - メリット: ダブルクリックで即ブラウザ表示可能
   - メリット: サーバー不要
   - メリット: 各ページを個別に開ける

**ビジュアル確認のみが目的**のため、簡単な直接埋め込み方式を採用。

#### 実施した作業
全9ファイルに以下を一括追加:

\`\`\`html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[フォルダ名]</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
[既存のコンテンツ]
</body>
</html>
\`\`\`

#### 処理対象ファイル
1. ホーム/index.html
2. サービス紹介/index.html
3. 料金/index.html
4. デザインサンプル/index.html
5. お問い合わせ/index.html
6. 資料請求/index.html
7. 初めての方へ/index.html
8. プライバシーポリシー/index.html
9. フッターメニュー/index.html

### 使用したTailwind CSS導入方法
**CDN版を使用** (`https://cdn.tailwindcss.com`)

**選択理由:**
- ビルド不要で即座に動作
- npmインストール不要
- 本番環境ではないため、CDNのデメリット(ファイルサイズ大、カスタマイズ不可)は問題なし
- レイアウト確認とブレストが目的のため最適

### 結果
- すべてのHTMLファイルがブラウザで正しく表示可能になった
- Tailwind CSSのスタイルが適用され、デザイン確認が可能
- ファイルをダブルクリックするだけで即座に確認できる

## 今後の展開
このHTMLは**レイアウト確認とブレスト専用**です。
本番環境では以下を推奨:
- Tailwind CSSのビルド版(npm経由)を使用
- 適切なHTML構造とメタタグの追加
- パフォーマンス最適化
- SEO対策
