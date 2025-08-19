#Calude Code プロジェクト設定

## KAMUI CODE 基本設定
- 画像・動画・3Dなど。生成完了したらURLダウンロードとopenをやること。
- ダウンロードは今いるディレクトリに。 
- 必ず得られた認証済URLのフルパスを利用（googleからの場合長い、falの場合は短い）。省略などしない。 
- I2v, i2iの際のインプットurlはgoogleからのものを使う。省略の無いように（*ファイルパスではない！）。
- 保存したファイルの場所は~からのフルパスで表示。
- 画像生成は1:1をデフォにして

## ファイルアップロード設定 
### FAL URLアップロード 
**必須**: ファイルをFAL URLに変換する際は`_KAMUI/helper/fal_upload_helper.py`を利用すること 

#### 使用方法 
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

適用場面 
- 動画生成API（Luma, Runway等）へのインプット 
- 画像生成APIへのインプット 
- 音声生成APIへのインプット 
- その他のFAL APIサービス利用時 

重要: 手動でのファイルアップロードやURL変換は行わず、必ず上記スクリプトを使用する 
```