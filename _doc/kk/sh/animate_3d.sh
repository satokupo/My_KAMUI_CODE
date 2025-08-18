#!/bin/bash

# 3Dモデルのアニメーション処理（リギング + アニメーション）
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
    echo "使用方法: $0 <original_model_task_id> [animation_type]"
    echo ""
    echo "引数:"
    echo "  original_model_task_id  - 元の3DモデルのタスクID"
    echo "  animation_type         - アニメーションタイプ（省略時: run）"
    echo ""
    echo "利用可能なアニメーション:"
    echo "  - preset:idle"
    echo "  - preset:walk"
    echo "  - preset:climb"
    echo "  - preset:jump"
    echo "  - preset:run"
    echo "  - preset:slash"
    echo "  - preset:shoot"
    echo "  - preset:hurt"
    echo "  - preset:fall"
    echo "  - preset:turn"
    echo ""
    echo "例: $0 cca40c57-bfcc-4d14-baac-e0e8d8de8a33 preset:walk"
    exit 1
}

# 引数チェック
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
fi

ORIGINAL_TASK_ID="$1"
ANIMATION_TYPE="${2:-preset:run}"  # デフォルトは run

# 環境変数チェック
if [ -z "$TRIPO_APIKEY" ]; then
    echo "エラー: TRIPO_APIKEY 環境変数が設定されていません"
    echo "export TRIPO_APIKEY=\"your_api_key\" を実行してください"
    exit 1
fi

echo "=== 3Dモデルアニメーション処理を開始します ==="
echo "元モデルタスクID: $ORIGINAL_TASK_ID"
echo "アニメーションタイプ: $ANIMATION_TYPE"

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
            echo "✓ 処理が完了しました！"
            echo "$POLL_RESPONSE"
            return 0
        elif [ "$STATUS" = "failed" ]; then
            echo "エラー: 処理に失敗しました"
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

# 1. リギング処理
echo "1. リギング処理を開始中..."
RIG_RESPONSE=$(curl -s -X POST 'https://api.tripo3d.ai/v2/openapi/task' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${TRIPO_APIKEY}" \
    -d "{\"type\": \"animate_rig\",\"original_model_task_id\": \"${ORIGINAL_TASK_ID}\",\"out_format\": \"glb\"}")

echo "リギングタスク作成レスポンス: $RIG_RESPONSE"

# リギングtask_idを抽出
RIG_TASK_ID=$(echo "$RIG_RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$RIG_TASK_ID" ]; then
    echo "エラー: リギングtask_idの取得に失敗しました"
    echo "レスポンス: $RIG_RESPONSE"
    exit 1
fi

echo "リギングTASK_ID: $RIG_TASK_ID"

# 2. リギング完了待機
echo "2. リギング完了をポーリング中..."
if ! poll_task "$RIG_TASK_ID"; then
    echo "リギング処理が失敗しました"
    exit 1
fi

# 3. アニメーション処理
echo "3. アニメーション処理を開始中..."
ANIMATE_RESPONSE=$(curl -s -X POST 'https://api.tripo3d.ai/v2/openapi/task' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${TRIPO_APIKEY}" \
    -d "{\"type\": \"animate_retarget\",\"original_model_task_id\": \"${RIG_TASK_ID}\",\"out_format\": \"glb\",\"animation\": \"${ANIMATION_TYPE}\"}")

echo "アニメーションタスク作成レスポンス: $ANIMATE_RESPONSE"

# アニメーションtask_idを抽出
ANIMATE_TASK_ID=$(echo "$ANIMATE_RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ANIMATE_TASK_ID" ]; then
    echo "エラー: アニメーションtask_idの取得に失敗しました"
    echo "レスポンス: $ANIMATE_RESPONSE"
    exit 1
fi

echo "アニメーションTASK_ID: $ANIMATE_TASK_ID"

# 4. アニメーション完了待機
echo "4. アニメーション完了をポーリング中..."
if poll_task "$ANIMATE_TASK_ID"; then
    echo "アニメーション処理が完了しました！"
    
    # 最終結果を取得してモデルURLを抽出
    FINAL_RESPONSE=$(curl -s "https://api.tripo3d.ai/v2/openapi/task/${ANIMATE_TASK_ID}" \
        -H "Authorization: Bearer ${TRIPO_APIKEY}")
    
    # result.model.urlを抽出（アニメーションの場合はpbr_modelではなくこちら）
    MODEL_URL=$(echo "$FINAL_RESPONSE" | grep -o '"url":"[^"]*"' | cut -d'"' -f4 | sed 's/\\//g')
    
    if [ -n "$MODEL_URL" ]; then
        echo "アニメーションモデルURL: $MODEL_URL"
        
        # モデルファイルをダウンロード
        ANIMATION_NAME=$(echo "$ANIMATION_TYPE" | sed 's/preset://')
        OUTPUT_FILE="animated_${ANIMATION_NAME}_${ANIMATE_TASK_ID}.glb"
        echo "アニメーションモデルをダウンロード中: $OUTPUT_FILE"
        curl -o "$OUTPUT_FILE" "$MODEL_URL"
        echo "✓ ダウンロード完了: $OUTPUT_FILE"
        
        echo "=== アニメーション処理が正常に完了しました ==="
        echo "出力ファイル: $OUTPUT_FILE"
    else
        echo "エラー: アニメーションモデルのURLが見つかりません"
        echo "レスポンス: $FINAL_RESPONSE"
        exit 1
    fi
else
    echo "アニメーション処理が失敗しました"
    exit 1
fi