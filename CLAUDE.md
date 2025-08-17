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
**必須**: ファイルをFAL URLに変換する際は`upload_to_fal.py`を利用すること 

#### 使用方法 
```bash 
# ファイルをFAL URLに変換 
python upload_to_fal.py [ファイルパス] 

# 例：動画ファイルをアップロード 
python upload_to_fal.py ./video.mp4 

# 例：画像ファイルをアップロード 
python upload_to_fal.py ./image.jpg

適用場面 
- 動画生成API（Luma, Runway等）へのインプット 
- 画像生成APIへのインプット 
- 音声生成APIへのインプット 
- その他のFAL APIサービス利用時 

重要: 手動でのファイルアップロードやURL変換は行わず、必ずupload_to_fal.pyスクリプトを使用する 
```