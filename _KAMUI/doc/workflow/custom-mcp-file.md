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
  - `mcp-kamui-code.json` (全MCPサーバーカタログ・約90種類)
  - `mcp-kamui-code-base.json` (必須ベース: file-upload, train, video-analysis)
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

**注意**: キーは必ず`mcpServers`（キャメルケース）を使用

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
`mcp-kamui-code-base.json`の内容（3サーバー）を必ず含める:
- `file-upload-kamui-fal` (ファイルアップロード)
- `train-kamui-flux-kontext` (モデルトレーニング)
- `video-analysis-kamui` (動画解析)

### 4. Kamui Code MCP選定
`mcp-kamui-code.json`から作業に必要なMCPをピックアップ:
1. ヒアリング内容に基づきカテゴリ（t2i, i2v等）を判断
2. 該当カテゴリのMCPを候補としてリストアップ
3. 連番と説明（description含む）をチャットで一覧表示
4. ユーザーの許可を得る

**選定例**:
- 画像生成作業 → t2i系（flux-srpo, seedream-v4, gemini-25-flash等）
- 動画生成作業 → t2v系, i2v系（kling-video, sora, wan等）
- 画像編集作業 → i2i系（kontext-max, qwen-edit-plus等）

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
- **JSON構造の遵守**: 必ず`mcpServers`（キャメルケース）を使用
- **必須ベースの追加**: `mcp-kamui-code-base.json`の3サーバーは常に含める
- **重複の回避**: ベースに含まれるサーバーを再度追加しない
- **説明の保持**: descriptionフィールドは必ず含める（⭐の数も保持）
