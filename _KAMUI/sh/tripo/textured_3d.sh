#!/bin/bash

# 3Dモデルのテクスチャ再生成処理（テキスト・画像対応）
# 環境変数 TRIPO_APIKEY が設定されている必要があります

set -e

# .envファイルから環境変数を読み込み
if [ -f .env ]; then
    echo ".envファイルから環境変数を読み込んでいます..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo "警告: .envファイルが見つかりません"
fi

# 使用方法
usage() {
    echo "使用方法: $0 <original_model_task_id> <texture_input> [options]"
    echo ""
    echo "引数:"
    echo "  original_model_task_id  - 元の3DモデルのタスクID"
    echo "  texture_input          - テクスチャプロンプトテキスト または 任意の文字列"
    echo ""
    echo "オプション:"
    echo "  --image <image_file>    - 画像ファイルを参照してテクスチャ生成"
    echo "  --style-image <path>    - スタイル参照用の画像ファイル"
    echo "  --pbr true|false        - PBRテクスチャを有効/無効 (デフォルト: true)"
    echo "  --quality standard|detailed  - テクスチャ品質 (デフォルト: standard)"
    echo "  --alignment original_image|geometry  - テクスチャ配置 (デフォルト: original_image)"
    echo "  --seed <number>         - テクスチャ生成用シード値"
    echo ""
    echo "例:"
    echo "  $0 abc123-def456-ghi789 'realistic bear fur texture, brown and fluffy'"
    echo "  $0 abc123-def456-ghi789 _ --image texture.jpg"
    echo "  $0 abc123-def456-ghi789 'metal texture' --style-image style.jpg --quality detailed"
    exit 1
}

# 引数チェック
if [ $# -lt 2 ]; then
    usage
fi

ORIGINAL_TASK_ID="$1"
TEXTURE_PROMPT="$2"

# オプション解析
PBR="true"
TEXTURE_QUALITY="standard"
TEXTURE_ALIGNMENT="original_image"
TEXTURE_SEED=""
IMAGE_FILE=""
STYLE_IMAGE=""
USE_IMAGE_MODE=false

shift 2  # 最初の2つの引数をスキップ

while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            IMAGE_FILE="$2"
            USE_IMAGE_MODE=true
            shift 2
            ;;
        --style-image)
            STYLE_IMAGE="$2"
            shift 2
            ;;
        --pbr)
            PBR="$2"
            shift 2
            ;;
        --quality)
            TEXTURE_QUALITY="$2"
            shift 2
            ;;
        --alignment)
            TEXTURE_ALIGNMENT="$2"
            shift 2
            ;;
        --seed)
            TEXTURE_SEED="$2"
            shift 2
            ;;
        *)
            echo "未知のオプション: $1"
            usage
            ;;
    esac
done

# 画像ファイルの存在確認
if [ "$USE_IMAGE_MODE" = true ] && [ ! -f "$IMAGE_FILE" ]; then
    echo "エラー: 画像ファイルが見つかりません: $IMAGE_FILE"
    exit 1
fi

# スタイル画像の存在確認
if [ -n "$STYLE_IMAGE" ] && [ ! -f "$STYLE_IMAGE" ]; then
    echo "エラー: スタイル画像ファイルが見つかりません: $STYLE_IMAGE"
    exit 1
fi

# 環境変数チェック
if [ -z "$TRIPO_APIKEY" ]; then
    echo "エラー: TRIPO_APIKEY 環境変数が設定されていません"
    echo "export TRIPO_APIKEY=\"your_api_key\" を実行してください"
    exit 1
fi

echo "=== 3Dモデルのテクスチャ再生成を開始します ==="
echo "元モデルタスクID: $ORIGINAL_TASK_ID"

if [ "$USE_IMAGE_MODE" = true ]; then
    echo "テクスチャ画像: $IMAGE_FILE"
else
    echo "テクスチャプロンプト: $TEXTURE_PROMPT"
fi

if [ -n "$STYLE_IMAGE" ]; then
    echo "スタイル画像: $STYLE_IMAGE"
fi

echo "PBR: $PBR"
echo "品質: $TEXTURE_QUALITY"
echo "配置: $TEXTURE_ALIGNMENT"
if [ -n "$TEXTURE_SEED" ]; then
    echo "シード値: $TEXTURE_SEED"
fi

# 画像アップロード機能（image_to_3d.shから流用）
upload_image() {
    local image_path="$1"
    echo "画像をアップロード中: $image_path"
    
    UPLOAD_RESPONSE=$(curl -s -X POST 'https://api.tripo3d.ai/v2/openapi/upload/sts' \
        -H 'Content-Type: multipart/form-data' \
        -H "Authorization: Bearer ${TRIPO_APIKEY}" \
        -F "file=@${image_path}")
    
    echo "アップロードレスポンス: $UPLOAD_RESPONSE"
    
    # image_tokenを抽出
    IMAGE_TOKEN=$(echo "$UPLOAD_RESPONSE" | grep -o '"image_token":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$IMAGE_TOKEN" ]; then
        echo "エラー: 画像アップロードに失敗しました"
        echo "レスポンス: $UPLOAD_RESPONSE"
        exit 1
    fi
    
    echo "✓ 画像アップロード完了: $IMAGE_TOKEN"
    echo "$IMAGE_TOKEN"
}

# ポーリング処理関数
poll_task() {
    local task_id="$1"
    local max_attempts=60  # 最大60回試行（5分）
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        echo "ポーリング試行 $attempt/$max_attempts..."
        
        POLL_RESPONSE=$(curl -s "https://api.tripo3d.ai/v2/openapi/task/${task_id}" \
            -H "Authorization: Bearer ${TRIPO_APIKEY}")
        
        # ステータスを確認
        STATUS=$(echo "$POLL_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        
        echo "現在のステータス: $STATUS"
        
        if [ "$STATUS" = "success" ]; then
            echo "✓ テクスチャ再生成が完了しました！"
            echo "$POLL_RESPONSE"
            return 0
        elif [ "$STATUS" = "failed" ]; then
            echo "エラー: テクスチャ再生成に失敗しました"
            echo "レスポンス: $POLL_RESPONSE"
            return 1
        else
            echo "待機中... (5秒後に再試行)"
            sleep 5
        fi
    done
    
    echo "エラー: タイムアウトしました（最大試行回数に達しました）"
    return 1
}

# 画像アップロード処理
if [ "$USE_IMAGE_MODE" = true ]; then
    TEXTURE_IMAGE_TOKEN=$(upload_image "$IMAGE_FILE")
fi

if [ -n "$STYLE_IMAGE" ]; then
    STYLE_IMAGE_TOKEN=$(upload_image "$STYLE_IMAGE")
fi

# JSONペイロード構築
JSON_PAYLOAD="{\"type\": \"texture_model\",\"original_model_task_id\": \"${ORIGINAL_TASK_ID}\","

# テクスチャプロンプト部分
if [ "$USE_IMAGE_MODE" = true ]; then
    JSON_PAYLOAD="${JSON_PAYLOAD}\"texture_prompt\": {\"image\": {\"type\": \"png\",\"file_token\": \"${TEXTURE_IMAGE_TOKEN}\"}},"
else
    JSON_PAYLOAD="${JSON_PAYLOAD}\"texture_prompt\": {\"text\": \"${TEXTURE_PROMPT}\"},"
fi

# スタイル画像がある場合
if [ -n "$STYLE_IMAGE_TOKEN" ]; then
    JSON_PAYLOAD="${JSON_PAYLOAD}\"style_image\": {\"type\": \"png\",\"file_token\": \"${STYLE_IMAGE_TOKEN}\"},"
fi

JSON_PAYLOAD="${JSON_PAYLOAD}\"pbr\": ${PBR},\"texture_quality\": \"${TEXTURE_QUALITY}\",\"texture_alignment\": \"${TEXTURE_ALIGNMENT}\""

# シード値がある場合は追加
if [ -n "$TEXTURE_SEED" ]; then
    JSON_PAYLOAD="${JSON_PAYLOAD},\"texture_seed\": ${TEXTURE_SEED}"
fi

JSON_PAYLOAD="${JSON_PAYLOAD}}"

echo "APIリクエストペイロード: $JSON_PAYLOAD"

# 1. テクスチャ再生成タスク作成
echo "1. テクスチャ再生成タスクを作成中..."
TEXTURE_RESPONSE=$(curl -s -X POST 'https://api.tripo3d.ai/v2/openapi/task' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${TRIPO_APIKEY}" \
    -d "$JSON_PAYLOAD")

echo "テクスチャタスク作成レスポンス: $TEXTURE_RESPONSE"

# task_idを抽出
TEXTURE_TASK_ID=$(echo "$TEXTURE_RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TEXTURE_TASK_ID" ]; then
    echo "エラー: テクスチャtask_idの取得に失敗しました"
    echo "レスポンス: $TEXTURE_RESPONSE"
    exit 1
fi

echo "テクスチャTASK_ID: $TEXTURE_TASK_ID"

# 2. テクスチャ再生成完了待機
echo "2. テクスチャ再生成完了をポーリング中..."
if poll_task "$TEXTURE_TASK_ID"; then
    echo "テクスチャ再生成処理が完了しました！"
    
    # 最終結果を取得してモデルURLを抽出
    FINAL_RESPONSE=$(curl -s "https://api.tripo3d.ai/v2/openapi/task/${TEXTURE_TASK_ID}" \
        -H "Authorization: Bearer ${TRIPO_APIKEY}")
    
    # result.model.urlを抽出
    MODEL_URL=$(echo "$FINAL_RESPONSE" | grep -o '"model":"[^"]*"' | cut -d'"' -f4 | sed 's/\\//g')
    
    # PBRモデルのURLも抽出を試行
    PBR_MODEL_URL=$(echo "$FINAL_RESPONSE" | grep -o '"pbr_model":"[^"]*"' | cut -d'"' -f4 | sed 's/\\//g')
    
    if [ -n "$MODEL_URL" ]; then
        echo "テクスチャ付きモデルURL: $MODEL_URL"
        
        # モデルファイルをダウンロード
        OUTPUT_FILE="textured_${TEXTURE_TASK_ID}.glb"
        echo "テクスチャ付きモデルをダウンロード中: $OUTPUT_FILE"
        curl -o "$OUTPUT_FILE" "$MODEL_URL"
        echo "✓ ダウンロード完了: $OUTPUT_FILE"
        
        # PBRモデルもダウンロード
        if [ -n "$PBR_MODEL_URL" ] && [ "$PBR" = "true" ]; then
            PBR_OUTPUT_FILE="textured_pbr_${TEXTURE_TASK_ID}.glb"
            echo "PBRテクスチャ付きモデルをダウンロード中: $PBR_OUTPUT_FILE"
            curl -o "$PBR_OUTPUT_FILE" "$PBR_MODEL_URL"
            echo "✓ PBRダウンロード完了: $PBR_OUTPUT_FILE"
        fi
        
        echo "=== テクスチャ再生成処理が正常に完了しました ==="
        echo "出力ファイル: $OUTPUT_FILE"
        if [ -n "$PBR_OUTPUT_FILE" ]; then
            echo "PBR出力ファイル: $PBR_OUTPUT_FILE"
        fi
    else
        echo "エラー: テクスチャ付きモデルのURLが見つかりません"
        echo "レスポンス: $FINAL_RESPONSE"
        exit 1
    fi
else
    echo "テクスチャ再生成処理が失敗しました"
    exit 1
fi