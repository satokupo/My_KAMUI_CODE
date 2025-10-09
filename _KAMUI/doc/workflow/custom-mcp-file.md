# 即席MCPファイル作成ワークフロー

## 目的
肥大化した`mcp-kamui-code.json`（90+のMCPサーバー）から、ユーザーの作業内容に必要なMCPサーバーだけを抽出し、軽量な一時用MCP設定ファイルを自動生成する。

## 概要
- 作業内容をヒアリングし、必要なKamui Code関連MCPサーバーを選定
- 必要に応じて開発ツール系MCPも追加
- 選定したMCPを統合し、一時用MCPファイルとして出力

---

## 設定情報

### 対象ファイル
- **書き換え対象**: `S:\MyProjects\KAMUI_CODE\_KAMUI\mcp\my-mcp-temp.json`
- **参照元ファイル**:
  - `mcp-kamui-code.json` (全MCPサーバーカタログ・約90種類 / 必須ベース: file-upload, train, video-analysis)
  - `my-mcp-devtool.json` (開発ツール: chrome-devtools, context7, serena)

### MCPカテゴリ（プレフィックス）
- **t2i**: Text-to-Image（テキストから画像生成）
- **i2i**: Image-to-Image（画像編集・変換）
- **t2v**: Text-to-Video（テキストから動画生成）
- **i2v**: Image-to-Video（画像から動画生成）
- **v2v**: Video-to-Video（動画編集・変換）
- **t2s/tts**: Text-to-Speech（音声合成）
- **t2m**: Text-to-Music（音楽生成）
- **v2a/v2sfx**: Video-to-Audio（動画から音声生成）
- **a2v**: Audio-to-Video（音声から動画生成）
- **i2i3d**: Image-to-3D（3Dモデル生成）
- **r2v**: Reference-to-Video（参照画像から動画生成）
- **s2v**: Speech-to-Video（音声から動画生成）
- **t2visual**: Text-to-Visual（テキストから図表・ビジュアル生成）
- その他: train（トレーニング）、video-analysis（動画解析）

### MCPファイル フォーマット
```json
{
  "mcpServers": {
    "{mcp-name}": {
      "type": "http",
      "url": "{endpoint-url}",
      "description": "{description}"
    }
  }
}
```

---

## 実行手順

### 1. 初期化
`my-mcp-temp.json`の`mcpServers`内の既存記述をすべて削除
```json
{
  "mcpServers": {}
}
```
※ファイル自体は維持、中身のみクリア

### 2. ヒアリング
ユーザーに作業内容を質問:
```
どのような作業を行いますか？
```

### 3. 必須ベースの追加
`mcp-kamui-code.json`から以下の汎用的に必要なMCPを**必ず**追加:
- `file-upload-kamui-fal` (ファイルアップロード - 各種API利用時に必要)
- `train-kamui-flux-kontext` (モデルトレーニング)
- `video-analysis-kamui` (動画解析)

### 4. Kamui Code MCP選定（優先度別）
`mcp-kamui-code.json`から作業に必要なMCPを選定:

#### 4-1. 選定基準
1. **プレフィックス判定**: ヒアリング内容からカテゴリ（t2i, i2v等）を判断
2. **説明文解析**: 各MCPの`description`フィールドを読み、作業内容との関連性を評価
3. **⭐評価考慮**: ⭐の数（1〜4）も参考にする（⭐⭐⭐以上は推奨度が高い）

#### 4-2. 優先度分類
選定したMCPを以下の3段階に分類:

**【必須】** - 作業に絶対必要なMCP
- プレフィックスと説明文が作業内容に直接合致するもの
- 例: 画像生成作業なら主要なt2i系MCP

**【推奨】** - あると便利なMCP
- 関連する周辺機能や補助的な処理に使えるもの
- 例: 画像生成後の編集用i2i系MCP、アップスケール用MCP

**【オプション】** - 場合によっては使える可能性があるMCP
- 間接的に関連するもの、発展的な用途に使えるもの

#### 4-3. ユーザーへの提示
優先度別に整理した一覧をチャットで表示（**2桁の連番**を付与）:
```
【必須】以下のMCPは必ず追加します:
01. {mcp-name} - {description}
02. {mcp-name} - {description}
...

【推奨】以下のMCPも追加することをおすすめします:
03. {mcp-name} - {description}
04. {mcp-name} - {description}
...

【オプション】必要に応じて以下も追加できます:
05. {mcp-name} - {description}
06. {mcp-name} - {description}
...
```

ユーザーの許可を得る（特に推奨・オプションについて取捨選択）
※連番を使うことで「03と05は不要」などの指示がしやすくなる

**選定例**:
- **画像生成作業**
  - 必須: t2i系（flux-srpo, seedream-v4, gemini-25-flash等）
  - 推奨: i2i系（編集用）、i2i-aura-sr（アップスケール）
- **動画生成作業**
  - 必須: t2v系, i2v系（kling-video, sora, wan等）
  - 推奨: v2v系（編集・加工）、v2a系（音声追加）
- **画像編集作業**
  - 必須: i2i系（kontext-max, qwen-edit-plus等）
  - 推奨: t2i系（再生成用）、i2i-aura-sr（アップスケール）

### 5. DevTools設定の確認
開発作業の有無を確認:
```
開発ツール（DevTools）は必要ですか？
```
- **必要な場合**: `my-mcp-devtool.json`の内容を追加
  - `chrome-devtools` (ブラウザ操作)
  - `context7` (コンテキスト管理)
  - `serena` (デスクトップアプリ)

### 6. ファイル生成
選定されたMCPサーバー設定を統合し、`my-mcp-temp.json`に書き込み

### 7. 確認
生成されたファイルの内容を表示し、ユーザーに確認

---

## 注意事項
- **必須ベースの追加**: 汎用3サーバー（file-upload, train, video-analysis）は常に含める
- **重複の回避**: 必須ベースに含まれるサーバーを再度追加しない
- **説明の保持**: descriptionフィールドは必ず含める（⭐の数も保持）
- **プレフィックスと説明の両方を確認**: カテゴリだけでなく説明文も読んで判断する
