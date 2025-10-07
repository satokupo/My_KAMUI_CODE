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
2. 任意のディレクトリに解凍（例: `Relume/2025-10-07_satokupo-design/`）

### 2. HTMLファイルを`index.html`にリネーム

RelumeからダウンロードしたHTMLファイルは日本語名やスペース含みの名前（例: `ホーム.html`, `Layout 324.html`）になっています。これを`index.html`にリネームします。

#### 基本的な使い方（1ファイルずつ）

```bash
# dry-runで確認（実際の変更は行わない）
.venv/Scripts/python.exe docs/helper/rename.py \
  --path "s:/MyProjects/KAMUI_CODE/Relume/2025-10-07_satokupo-design/01_ホーム/ホーム.html" \
  --new-name "index.html" \
  --dry-run \
  --verbose

# 本実行
.venv/Scripts/python.exe docs/helper/rename.py \
  --path "s:/MyProjects/KAMUI_CODE/Relume/2025-10-07_satokupo-design/01_ホーム/ホーム.html" \
  --new-name "index.html" \
  --verbose
```

**オプション**:
- `--path`: リネーム対象のファイルパス
- `--new-name`: 新しいファイル名（`index.html`固定）
- `--dry-run`: 実際の変更を行わず、実行内容のみ表示
- `--verbose`: 詳細なログを出力

**詳細**: `docs/初期フロー.md` の「2. HTMLファイルのリネーム」を参照

### 3. セットアップスクリプト実行

```bash
# 自動セットアップスクリプト実行
.venv/Scripts/python.exe docs/helper/setup_relume_project.py <ページディレクトリパス>

# 例
.venv/Scripts/python.exe docs/helper/setup_relume_project.py "s:/MyProjects/KAMUI_CODE/Relume/2025-10-07_satokupo-design/01_ホーム"
```

スクリプトは以下を自動で実行:
1. `docs/helper/setup_templates/`からディレクトリ構造とファイルをコピー
   - `assets/js/main.js`（features/自動読込コード付き）
   - `assets/style/base.css`（CSSネストルール案内コメント付き）
   - `assets/style/custom.css`（CSSネストルール案内コメント付き）
   - 各種ディレクトリ（features/, screenshots/, ai-workbench/等）
2. `index.html`にHTML基本タグ追加とTailwind CDN読み込み
3. セクション抽出とID割り当て（対話式）

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
- 基本デザインは`base.css`ファイルで上書き
- カスタムデザインは`custom.css`ファイルで上書き
- CSSネストで優先度を制御

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
