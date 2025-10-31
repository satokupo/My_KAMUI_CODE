# 背景透過処理ツール

rembgライブラリを使用して画像の背景を透明にするPythonスクリプトです。

## セットアップ

```bash
# 依存関係をインストール
pip install -r requirements.txt
```

## 使用方法

### 基本的な使用方法
```bash
# 入力画像のみ指定（出力は自動命名）
python background_remover.py input_image.jpg

# 出力ファイル名も指定
python background_remover.py input_image.jpg output_transparent.png

# モデルを指定
python background_remover.py input_image.jpg --model u2netp
```

### Claude Codeでの使用例
```bash
# Claude Codeで実行する場合
python S:/MyProjects/KAMUI_CODE/generate/2025-09-11_背景抜き/background_remover.py your_image.jpg
```

## 利用可能なモデル

- `u2net` (デフォルト): 汎用的で高精度
- `u2netp`: 軽量版、高速処理
- `silueta`: 人物に特化
- `isnet-general-use`: 一般用途向けの新しいモデル

## 出力形式

- 出力は常にPNG形式（透明度をサポート）
- 元のファイル名に `_transparent` を付加して保存（出力パス未指定時）

## 注意事項

- 初回実行時はモデルのダウンロードが必要（数百MB）
- GPU対応環境ではより高速に処理可能
- 大きな画像ファイルは処理に時間がかかります