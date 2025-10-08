# Relume Wireframe Brushup Project

## 概要

Relume wireframeツールから出力されたTailwind CSSベースのHTMLを、デザイン調整・機能追加を行いながらブラッシュアップするプロジェクト。

## ディレクトリ構成

```
<ページディレクトリ>/
├── assets/
│   ├── js/
│   │   ├── main.js           # エントリーポイント(features/を自動読込)
│   │   └── features/         # 機能別モジュール
│   ├── style/                # CSS (base.css,custom.css)
│   └── images/               # 画像アセット
├── screenshots/              # AI検証用スクリーンショット
├── temp/                     # 一時ファイル
└── docs/
    ├── _README.md            # このファイル
    └── ai-workbench/         # AIワークスペース(自由使用)
```

### 各ディレクトリの役割

#### `assets/`
レイアウト調整に必要な全てのアセット(CSS/JS/画像)を格納。

- **`js/main.js`** - エントリーポイント。`features/`配下のモジュールを自動検出・読込
- **`js/features/`** - 機能別モジュール置き場。追加するだけで`main.js`が自動認識
- **`style/`** - `base.css`で基本のスタイル（ユーティリティ含む）を指定,`custom.css`を利用してセクションごとのスタイルを作成
- **`images/`** - デザイン調整で使用する画像ファイル

#### `screenshots/`
レイアウト調整時にAIがMCP Chrome DevToolsで自動撮影したスクリーンショットを保存。

- 目的: AIが視覚的にレイアウトを検証しながら修正を行う
- 命名: `YYYYMMDD_HHMM_section-name.png` など、タイムスタンプ推奨

#### `temp/`
一時的なファイル置き場。作業中の中間ファイルなど。

#### `docs/`
プロジェクト文書とAIワークスペース。

- **永続的な文書**: `_README.md`、`初期フロー.md` など
- **`ai-workbench/`** - AIが自由に使えるワークスペース
  - 作業ログ、一時メモ、検証結果、任意のファイル構成が可能
  - タイムスタンプ付きログ推奨: `YYYYMMDD_HHMM_task-description.md`

## セットアップ

### 1. Relumeからzipをダウンロード・解凍
1. Relumeからプロジェクトzipファイルをダウンロード
2. 任意のディレクトリに解凍（例: `Relume/2025-10-08_satokupo-design-test/`）

**注意**: Relumeから出力されるディレクトリ構造は以下の通り:
- ディレクトリ名: 日本語名またはスペース含み（例: `ホーム/`, `初めての方へ/`, `Layout 324/`）
- 各ディレクトリ内: `index.html`が既に配置済み

### 2. ページ連番付与

ページディレクトリに連番を付与します（ワークフロー順序に従う）。

```bash
.venv/Scripts/python.exe Relume/docs/helper/rename.py \
  --root-dir "プロジェクトルート" \
  --mapping '{"ホーム":"01_ホーム","サービス紹介":"02_サービス紹介",...}'
```

### 3. セットアップスクリプト実行

各ページのセクション構成を聞き取り後、セットアップを実行します。

```bash
# 単一ページ処理（ヘッダーナビ・フッター除く）
.venv/Scripts/python.exe docs/helper/setup_relume_project.py \
  --page-dir "<ページディレクトリパス>" \
  --sections "section1,section2:full-wide,section3:wide,..."

# 例：幅指定あり
.venv/Scripts/python.exe docs/helper/setup_relume_project.py \
  --page-dir "s:/MyProjects/KAMUI_CODE/Relume/2025-10-08_satokupo-design-test/copy-of-ホームページ作成サービス/01_ホーム" \
  --sections "hero:full-wide,empathy-section,mini-benefit:full-wide,cta-section"
```

**幅指定の形式:**
- `section-name:full-wide` → フルワイド（画面幅いっぱい）
- `section-name:wide` → 少し広め（サイト幅まで）
- `section-name` → 通常幅（コンテンツ幅）

スクリプトは以下を自動で実行:
1. 最初の`<section>`を`<header>`でラップ（ヘッダーナビ化）
2. `docs/helper/setup_templates/`からディレクトリ構造とファイルをコピー
   - `assets/js/main.js`（features/自動読込コード付き）
   - `assets/style/base.css`（ユーティリティクラス・レスポンシブ設定付き）
   - `assets/style/custom.css`（セクション別スタイル記述用）
   - 各種ディレクトリ（features/, screenshots/, ai-workbench/等）
3. `index.html`にHTML基本タグ追加とTailwind CDN読み込み
4. コンテンツエリア内の`<section>`にID付与と幅指定クラス追加
   - ヘッダーナビ・フッターはID付与対象外

## CSS設計ルール

### ネストルール遵守

**必須**: 全てのスタイルはセクションIDでネストし、他セクションへのスタイル漏れを防ぐ。

```css
/* ✅ 正しい例 */
#section-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  .hero-title {
    font-size: 3rem;
    font-weight: bold;
  }

  .hero-subtitle {
    font-size: 1.25rem;
    color: #f0f0f0;
  }
}

/* ❌ 間違った例 - セクションIDなしでネスト */
.hero-title {
  font-size: 3rem; /* 他のセクションにも影響する可能性 */
}
```

### Tailwind CSS との共存

- Relume出力のTailwind CSSはそのまま維持
- `base.css`ファイル:
  - サイト全体の基本設定（カラー変数、フォント、サイト幅等）
  - ユーティリティクラス（`full-wide`, `wide`, `wide-inner`）
  - レスポンシブ設定（スマホ対応）
- `custom.css`ファイル:
  - セクション別のカスタムスタイル
  - セクションIDでネストして記述
- CSSネストで優先度を制御

### ユーティリティクラス（base.cssで定義）

#### `full-wide` - フルワイドセクション
画面幅いっぱいにセクションを広げます。インナーブロックはコンテンツ幅（ブログ幅）になります。

```html
<section class="full-wide" id="hero">
  <div class="container">
    <div>コンテンツ幅</div>
    <div class="wide-inner">サイト幅まで広げる</div>
  </div>
</section>
```

#### `wide` - 少し広めセクション
サイト幅までセクションを広げます。インナーブロックも連動して広がります。

```html
<section class="wide" id="features">
  <div class="container">サイト幅</div>
</section>
```

#### `wide-inner` - インナーブロック拡張
`full-wide`セクション内で、特定のインナーブロックをサイト幅まで広げます。

```css
/* base.cssでの定義 */
section.full-wide > .container > div:not(.wide-inner) {
  /* コンテンツ幅に制限 */
}
```

## JavaScript設計

### エントリーポイント: `main.js` (自動読込方式)

`features/`ディレクトリ配下のモジュールを自動検出・実行。

**実装例**:
```javascript
// assets/js/main.js
const modules = import.meta.glob('./features/*.js', { eager: true });

document.addEventListener('DOMContentLoaded', () => {
  Object.values(modules).forEach(module => {
    if (module.init && typeof module.init === 'function') {
      module.init();
    }
  });
});
```

### 機能モジュールの追加方法

`features/`に新しい`.js`ファイルを作成するだけで自動読込。

**例: `assets/js/features/carousel.js`**
```javascript
export function init() {
  console.log('Carousel initialized');
  // カルーセル機能の実装
}
```

**例: `assets/js/features/modal.js`**
```javascript
export function init() {
  console.log('Modal initialized');
  // モーダル機能の実装
}
```

### ディレクトリ構造

```
assets/js/
├── main.js              # エントリーポイント(自動読込)
└── features/            # 機能別モジュール(追加するだけでOK)
    ├── carousel.js
    ├── modal.js
    └── smooth-scroll.js
```

## AI作業時のガイドライン

### スクリーンショット撮影

レイアウト調整時は`screenshots/`にタイムスタンプ付きで保存:

```bash
# MCP Chrome DevTools経由で自動撮影
# ファイル名例: 20251007_1430_hero-section.png
```

### AIワークスペース利用

`docs/ai-workbench/`は自由に使える作業領域:

- **ログ記録**: タイムスタンプ付き推奨 (`YYYYMMDD_HHMM_task.md`)
- **一時メモ**: 検証結果、ToDo、アイデア等
- **任意構成**: サブディレクトリ作成も自由

**ログ例: `docs/ai-workbench/20251007_1430_hero-gradient.md`**
```markdown
# Hero Section グラデーション調整

**対象**: #section-hero
**内容**:
- グラデーション角度135度に変更
- 色: #667eea → #764ba2

**スクリーンショット**: `../screenshots/20251007_1430_hero.png`
```

## 技術スタック

- **HTML**: Relume出力(Tailwind CSS組み込み)
- **CSS**: Modern CSS Nesting + Tailwind CSS
- **JavaScript**: ES6 Modules
- **開発環境**: Python 3.x (仮想環境 `.venv`)
- **AI検証**: MCP Chrome DevTools

## 注意事項

- CSSはセクションIDでネスト必須(スタイル漏れ防止)
- JavaScriptはモジュール分割を意識
- AI作業ログは必ずタイムスタンプ付きで記録
- 画像などのバイナリファイルは`assets/images/`に集約
