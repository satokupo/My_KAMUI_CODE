#!/bin/bash  # シェルスクリプトの実行環境を指定

# Image to 3D処理とポーリング処理  # スクリプトの目的を説明
# 環境変数 TRIPO_APIKEY が設定されている必要があります  # 必要な環境変数の説明

set -e  # エラーが発生したらスクリプトを即座に終了する設定

# .envファイルから環境変数を読み込み
if [ -f .env ]; then
    echo ".envファイルから環境変数を読み込んでいます..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo "警告: .envファイルが見つかりません"
fi

# 使用方法  # ヘルプ表示用の関数定義開始
usage() {  # 正しい使い方を表示する関数
    echo "使用方法: $0 <image_file_path> [--no-pbr]"  # スクリプトの使い方を表示
    echo ""
    echo "オプション:"
    echo "  --no-pbr    PBR（光沢）を無効にして、マットな仕上がりにする"
    echo ""
    echo "例: $0 night.png"  # 具体的な実行例を表示
    echo "例: $0 night.png --no-pbr"  # PBR無効化の例
    exit 1  # エラーコード1でスクリプトを終了
}

# 引数チェック  # コマンドライン引数の数を確認
if [ $# -lt 1 ] || [ $# -gt 2 ]; then  # 引数が1個または2個でない場合
    usage  # 使用方法を表示して終了
fi

IMAGE_FILE="$1"  # 第1引数（画像ファイルパス）を変数に保存
USE_PBR="true"  # デフォルトはPBR有効

# オプション解析
if [ $# -eq 2 ] && [ "$2" = "--no-pbr" ]; then
    USE_PBR="false"
    echo "PBRを無効にしました（マットな仕上がり）"
fi

# 環境変数チェック  # API キーが設定されているか確認
if [ -z "$TRIPO_APIKEY" ]; then  # TRIPO_APIKEY が空文字列または未設定の場合
    echo "エラー: TRIPO_APIKEY 環境変数が設定されていません"  # エラーメッセージを表示
    echo "export TRIPO_APIKEY=\"your_api_key\" を実行してください"  # 解決方法を表示
    exit 1  # エラーコード1でスクリプトを終了
fi

# ファイル存在チェック  # 指定された画像ファイルが存在するか確認
if [ ! -f "$IMAGE_FILE" ]; then  # ファイルが存在しない場合
    echo "エラー: ファイル '$IMAGE_FILE' が見つかりません"  # エラーメッセージを表示
    exit 1  # エラーコード1でスクリプトを終了
fi


# 1. 画像アップロード  # 第1段階：画像をTripo APIにアップロード
echo "1. 画像をアップロード中..."  # 進行状況を表示
UPLOAD_RESPONSE=$(curl -s -X POST 'https://api.tripo3d.ai/v2/openapi/upload/sts' \
    -H 'Content-Type: multipart/form-data' \
    -H "Authorization: Bearer ${TRIPO_APIKEY}" \
    -F "file=@${IMAGE_FILE}")

echo "アップロードレスポンス: $UPLOAD_RESPONSE"  # API からの応答を表示

# image_tokenを抽出  # API 応答から画像トークンを取り出す
IMAGE_TOKEN=$(echo "$UPLOAD_RESPONSE" | grep -o '"image_token":"[^"]*"' | cut -d'"' -f4)  # JSON から image_token の値を抽出

if [ -z "$IMAGE_TOKEN" ]; then  # 画像トークンの取得に失敗した場合
    echo "エラー: image_tokenの取得に失敗しました"  # エラーメッセージを表示
    echo "レスポンス: $UPLOAD_RESPONSE"  # デバッグ用に応答内容を表示
    exit 1  # エラーコード1でスクリプトを終了
fi

echo "IMAGE_TOKEN: $IMAGE_TOKEN"  # 取得した画像トークンを表示

# 2. 3Dモデル生成タスク作成  # 第2段階：3Dモデル生成処理を開始
echo "2. 3Dモデル生成タスクを作成中..."  # 進行状況を表示
TASK_RESPONSE=$(curl -s -X POST 'https://api.tripo3d.ai/v2/openapi/task' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${TRIPO_APIKEY}" \
    -d "{\"type\": \"image_to_model\",\"file\": {\"type\": \"png\",\"file_token\": \"${IMAGE_TOKEN}\"},\"pbr\": ${USE_PBR}}")

echo "タスク作成レスポンス: $TASK_RESPONSE"  # API からの応答を表示

# task_idを抽出  # API 応答からタスクID を取り出す
TASK_ID=$(echo "$TASK_RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)  # JSON から task_id の値を抽出

if [ -z "$TASK_ID" ]; then  # タスクID の取得に失敗した場合
    echo "エラー: task_idの取得に失敗しました"  # エラーメッセージを表示
    echo "レスポンス: $TASK_RESPONSE"  # デバッグ用に応答内容を表示
    exit 1  # エラーコード1でスクリプトを終了
fi

echo "TASK_ID: $TASK_ID"  # 取得したタスクID を表示

# 3. ポーリング処理  # 第3段階：モデル生成完了まで定期的に状況確認
echo "3. モデル生成完了をポーリング中..."  # 進行状況を表示

poll_task() {  # タスクの完了を監視する関数定義
    local task_id="$1"  # 関数の第1引数（タスクID）をローカル変数に保存
    local max_attempts=60  # 最大試行回数を60回に設定（約5分間）
    local attempt=0  # 現在の試行回数を0で初期化
    
    while [ $attempt -lt $max_attempts ]; do  # 最大試行回数に達するまでループ
        attempt=$((attempt + 1))  # 試行回数を1増やす
        echo "ポーリング試行 $attempt/$max_attempts..."  # 現在の試行回数を表示
        
        POLL_RESPONSE=$(curl -s "https://api.tripo3d.ai/v2/openapi/task/${task_id}" \
            -H "Authorization: Bearer ${TRIPO_APIKEY}")
        
        # ステータスを確認  # API 応答からタスクの状況を取得
        STATUS=$(echo "$POLL_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)  # JSON から status の値を抽出
        
        echo "現在のステータス: $STATUS"  # 現在のタスク状況を表示
        
        if [ "$STATUS" = "success" ]; then  # タスクが正常に完了した場合
            echo "✓ モデル生成が完了しました！"  # 完了メッセージを表示
            
            # modelのURLを抽出（PBR有無に関わらず）  # 生成されたモデルのダウンロードURL を取得
            MODEL_URL=$(echo "$POLL_RESPONSE" | grep -o '"url":"https://[^"]*\.glb[^"]*"' | cut -d'"' -f4 | sed 's/\\//g')  # JSON からモデルURL を抽出し、バックスラッシュを除去
            
            if [ -n "$MODEL_URL" ]; then  # モデルURL が正常に取得できた場合
                echo "モデルURL: $MODEL_URL"  # モデルのダウンロードURL を表示
                
                # モデルファイルをダウンロード  # 生成されたモデルファイルをローカルに保存
                OUTPUT_FILE="model_${task_id}.glb"  # 出力ファイル名をタスクID 付きで生成
                echo "モデルをダウンロード中: $OUTPUT_FILE"  # ダウンロード開始メッセージを表示
                curl -o "$OUTPUT_FILE" "$MODEL_URL"  # curl でモデルファイルをダウンロード
                echo "✓ ダウンロード完了: $OUTPUT_FILE"  # ダウンロード完了メッセージを表示
                return 0  # 成功を示すコード0で関数終了
            else
                echo "エラー: pbr_modelのURLが見つかりません"  # URL 取得失敗のエラーメッセージ
                echo "レスポンス: $POLL_RESPONSE"  # デバッグ用に応答内容を表示
                return 1  # エラーを示すコード1で関数終了
            fi
        elif [ "$STATUS" = "failed" ]; then  # タスクが失敗した場合
            echo "エラー: モデル生成に失敗しました"  # 失敗メッセージを表示
            echo "レスポンス: $POLL_RESPONSE"  # デバッグ用に応答内容を表示
            return 1  # エラーを示すコード1で関数終了
        else  # タスクがまだ実行中の場合
            echo "待機中... (5秒後に再試行)"  # 待機メッセージを表示
            sleep 5  # 5秒間処理を停止
        fi
    done  # ループ終了
    
    echo "エラー: タイムアウトしました（最大試行回数に達しました）"  # タイムアウトエラーメッセージ
    return 1  # エラーを示すコード1で関数終了
}

# ポーリング実行  # 作成したタスクの完了を監視開始
if poll_task "$TASK_ID"; then  # ポーリング関数を実行し、成功した場合
    echo "=== Image to 3D処理が正常に完了しました ==="  # 全体処理の成功メッセージ
else  # ポーリング関数が失敗した場合
    echo "=== Image to 3D処理が失敗しました ==="  # 全体処理の失敗メッセージ
    exit 1  # エラーコード1でスクリプトを終了
fi