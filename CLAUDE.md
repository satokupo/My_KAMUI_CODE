# Claude Code プロジェクト設定

## メディア生成・処理ワークフロー

### 生成処理
- 画像・動画・音声・3Dなど。生成完了したら必ずローカルに自動保存すること。
- デフォルトのアスペクト比は4:3にすること
- 生成する画像タイトルは`{01からのナンバリング}_{title}_{使用したAIモデル名}`とすること
- タイトル内の変数の中では半角英数字と`-`ハイフン記号のみ許可する

### 保存処理
#### 保存場所の優先順位
1. **最優先**: ユーザーがチャットで明確に指示した場所
2. **2番目**: 提供された指示書・要件定義書内に記載された保存場所
3. **3番目**: 提供された指示書・要件定義書と同じ階層
4. **最後**: プロジェクトルート（S:/MyProjects/KAMUI_CODE/）

#### 保存時の処理
- 保存したファイルの場所は~からのフルパスで表示
- 必ず得られた認証済URLのフルパスを利用（googleからの場合長い、falの場合は短い）。省略などしない

### アップロード処理
#### FAL URLアップロード
**必須**: ファイルをFAL URLに変換する際は`_KAMUI/helper/fal_upload_helper.py`を利用すること

##### 使用方法
```bash
# ファイルをFAL URLに変換 (ファイルパス: S:/MyProjects/KAMUI_CODE/_KAMUI/helper/fal_upload_helper.py)
python _KAMUI/helper/fal_upload_helper.py [ファイルパス] 

# または実行権限付きで直接実行
./_KAMUI/helper/fal_upload_helper.py [ファイルパス]

# MCP連携用 (ファイルパス: S:/MyProjects/KAMUI_CODE/_KAMUI/helper/local_fal_upload.py)
python _KAMUI/helper/local_fal_upload.py [ファイルパス]

# 例：動画ファイルをアップロード 
python _KAMUI/helper/fal_upload_helper.py ./video.mp4 

# 例：画像ファイルをアップロード 
python _KAMUI/helper/fal_upload_helper.py ./image.jpg
```

##### 適用場面
- 動画生成API（Luma, Runway等）へのインプット 
- 画像生成APIへのインプット 
- 音声生成APIへのインプット 
- その他のFAL APIサービス利用時 

**重要**: 手動でのファイルアップロードやURL変換は行わず、必ず上記スクリプトを使用する

##### URL利用時の注意点
- i2v, i2iの際のインプットurlはgoogleからのものを使う。省略の無いように（**ファイルパスではない！**）

## 要件定義・ドキュメント作成

### ビジュアライズ要件定義
- `requirement-docs` の作成場所は資料の要件定義と同じ階層に作成する（ユーザーから明確な指示があればそれに従う）
- 元になる資料が存在しない場合は、プロジェクトルートに作成する
- `requirement-docs` 内に自動生成時に `.git` ディレクトリが作られる場合がある → gitリポジトリからの pull 完了後に `.git` を `.git-archived` にリネームし、親リポジトリ（KAMUI_CODE）配下で一元管理できるようにする

## 基本設定

### 文字コード
- 指示がない限りUTF-8を利用すること