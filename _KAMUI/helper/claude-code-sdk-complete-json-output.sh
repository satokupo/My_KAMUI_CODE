#!/bin/bash
# Claude Code SDK Complete JSON Output Script
# 全てのJSON情報を抜けなく出力する

# デフォルト値設定
MAX_TURNS=${MAX_TURNS:-15}

npx @anthropic-ai/claude-code -p "$PROMPT" \
  --system-prompt "$SYSTEM_PROMPT" \
  --max-turns $MAX_TURNS \
  --permission-mode bypassPermissions \
  --verbose \
  --output-format stream-json \
  2>&1 | while IFS= read -r line; do
    # 時刻を取得
    TIMESTAMP="[$(date '+%H:%M:%S')]"
    
    # JSON形式かチェック
    if echo "$line" | jq -e 'type == "object"' > /dev/null 2>&1; then
      MESSAGE_TYPE=$(echo "$line" | jq -r '.type // "unknown"')
      
      case "$MESSAGE_TYPE" in
        "system")
          SUBTYPE=$(echo "$line" | jq -r '.subtype // "unknown"')
          if [ "$SUBTYPE" = "init" ]; then
            # 全情報を出力
            SESSION_ID=$(echo "$line" | jq -r '.session_id // "N/A"')
            MODEL=$(echo "$line" | jq -r '.model // "N/A"')
            CWD=$(echo "$line" | jq -r '.cwd // "N/A"')
            TOOLS=$(echo "$line" | jq -r '.tools // [] | join(", ")')
            MCP_SERVERS=$(echo "$line" | jq -r '.mcp_servers // [] | join(", ")')
            PERMISSION_MODE=$(echo "$line" | jq -r '.permissionMode // "N/A"')
            API_KEY_SOURCE=$(echo "$line" | jq -r '.apiKeySource // "N/A"')
            
            echo "🎯 SYSTEM INIT $TIMESTAMP:"
            echo "   └── 🆔 SESSION_ID: $SESSION_ID"
            echo "   └── 🤖 MODEL: $MODEL"
            echo "   └── 📁 CWD: $CWD"
            echo "   └── 🛠️ TOOLS: $TOOLS"
            echo "   └── 🔌 MCP_SERVERS: $MCP_SERVERS"
            echo "   └── 🔒 PERMISSION_MODE: $PERMISSION_MODE"
            echo "   └── 🔑 API_KEY_SOURCE: $API_KEY_SOURCE"
          else
            # その他のsystemメッセージ
            echo "🎯 SYSTEM_$SUBTYPE $TIMESTAMP:"
            echo "$line" | jq -r 'to_entries[] | "   └── \(.key): \(.value)"'
          fi
          ;;
        
        "assistant")
          MSG_ID=$(echo "$line" | jq -r '.message.id // "N/A"')
          MSG_TYPE=$(echo "$line" | jq -r '.message.type // "N/A"')
          MSG_ROLE=$(echo "$line" | jq -r '.message.role // "N/A"')
          MSG_MODEL=$(echo "$line" | jq -r '.message.model // "N/A"')
          STOP_REASON=$(echo "$line" | jq -r '.message.stop_reason // "N/A"')
          STOP_SEQUENCE=$(echo "$line" | jq -r '.message.stop_sequence // "N/A"')
          
          # Usage情報
          USAGE_INPUT=$(echo "$line" | jq -r '.message.usage.input_tokens // 0')
          USAGE_OUTPUT=$(echo "$line" | jq -r '.message.usage.output_tokens // 0')
          USAGE_CACHE_CREATION=$(echo "$line" | jq -r '.message.usage.cache_creation_input_tokens // 0')
          USAGE_CACHE_READ=$(echo "$line" | jq -r '.message.usage.cache_read_input_tokens // 0')
          SERVICE_TIER=$(echo "$line" | jq -r '.message.usage.service_tier // "N/A"')
          
          # Content情報
          CONTENT_COUNT=$(echo "$line" | jq -r '.message.content | length')
          
          echo "🤖 ASSISTANT $TIMESTAMP:"
          echo "   └── 🆔 MESSAGE_ID: $MSG_ID"
          echo "   └── 📋 TYPE: $MSG_TYPE"
          echo "   └── 👤 ROLE: $MSG_ROLE"
          echo "   └── 🤖 MODEL: $MSG_MODEL"
          echo "   └── 🛑 STOP_REASON: $STOP_REASON"
          echo "   └── 🔚 STOP_SEQUENCE: $STOP_SEQUENCE"
          echo "   └── 🪙 USAGE_INPUT: $USAGE_INPUT"
          echo "   └── 🪙 USAGE_OUTPUT: $USAGE_OUTPUT"
          echo "   └── 🪙 USAGE_CACHE_CREATION: $USAGE_CACHE_CREATION"
          echo "   └── 🪙 USAGE_CACHE_READ: $USAGE_CACHE_READ"
          echo "   └── 🏷️ SERVICE_TIER: $SERVICE_TIER"
          echo "   └── 📄 CONTENT_COUNT: $CONTENT_COUNT"
          
          # 各コンテンツを詳細出力
          for i in $(seq 0 $((CONTENT_COUNT - 1))); do
            CONTENT_TYPE=$(echo "$line" | jq -r ".message.content[$i].type // \"unknown\"")
            if [ "$CONTENT_TYPE" = "text" ]; then
              TEXT_CONTENT=$(echo "$line" | jq -r ".message.content[$i].text // \"N/A\"")
              echo "   └── 📝 CONTENT[$i]_TEXT:"
              echo -e "$TEXT_CONTENT" | sed 's/^/        /'
            elif [ "$CONTENT_TYPE" = "tool_use" ]; then
              TOOL_ID=$(echo "$line" | jq -r ".message.content[$i].id // \"N/A\"")
              TOOL_NAME=$(echo "$line" | jq -r ".message.content[$i].name // \"N/A\"")
              echo "   └── 🛠️ CONTENT[$i]_TOOL_ID: $TOOL_ID"
              echo "   └── 🛠️ CONTENT[$i]_TOOL_NAME: $TOOL_NAME"
              echo "   └── 🛠️ CONTENT[$i]_TOOL_INPUT:"
              # JSONオブジェクトかどうかをチェック
              if echo "$line" | jq -e ".message.content[$i].input | type == \"object\"" > /dev/null 2>&1; then
                echo "$line" | jq -r ".message.content[$i].input | to_entries[] | \"        \(.key): \(.value)\"" | while IFS= read -r entry; do
                  echo -e "$entry"
                done
              else
                TOOL_INPUT_RAW=$(echo "$line" | jq -r ".message.content[$i].input // \"N/A\"")
                echo -e "$TOOL_INPUT_RAW" | sed 's/^/        /'
              fi
            fi
          done
          
          # Parent tool use ID
          PARENT_TOOL_USE_ID=$(echo "$line" | jq -r '.parent_tool_use_id // "N/A"')
          SESSION_ID=$(echo "$line" | jq -r '.session_id // "N/A"')
          echo "   └── 🔗 PARENT_TOOL_USE_ID: $PARENT_TOOL_USE_ID"
          echo "   └── 🆔 SESSION_ID: $SESSION_ID"
          ;;
        
        "user")
          MSG_ROLE=$(echo "$line" | jq -r '.message.role // "N/A"')
          CONTENT_COUNT=$(echo "$line" | jq -r '.message.content | length')
          PARENT_TOOL_USE_ID=$(echo "$line" | jq -r '.parent_tool_use_id // "N/A"')
          SESSION_ID=$(echo "$line" | jq -r '.session_id // "N/A"')
          
          echo "👤 USER $TIMESTAMP:"
          echo "   └── 👤 ROLE: $MSG_ROLE"
          echo "   └── 📄 CONTENT_COUNT: $CONTENT_COUNT"
          echo "   └── 🔗 PARENT_TOOL_USE_ID: $PARENT_TOOL_USE_ID"
          echo "   └── 🆔 SESSION_ID: $SESSION_ID"
          
          # 各コンテンツを詳細出力
          for i in $(seq 0 $((CONTENT_COUNT - 1))); do
            CONTENT_TYPE=$(echo "$line" | jq -r ".message.content[$i].type // \"unknown\"")
            if [ "$CONTENT_TYPE" = "tool_result" ]; then
              TOOL_USE_ID=$(echo "$line" | jq -r ".message.content[$i].tool_use_id // \"N/A\"")
              TOOL_CONTENT=$(echo "$line" | jq -r ".message.content[$i].content // \"N/A\"" | head -10)
              IS_ERROR=$(echo "$line" | jq -r ".message.content[$i].is_error // false")
              echo "   └── 🔧 CONTENT[$i]_TOOL_USE_ID: $TOOL_USE_ID"
              echo "   └── 🔧 CONTENT[$i]_IS_ERROR: $IS_ERROR"
              echo "   └── 🔧 CONTENT[$i]_CONTENT:"
              echo -e "$TOOL_CONTENT" | sed 's/^/        /'
            fi
          done
          ;;
        
        "result")
          SUBTYPE=$(echo "$line" | jq -r '.subtype // "N/A"')
          DURATION=$(echo "$line" | jq -r '.duration_ms // "N/A"')
          NUM_TURNS=$(echo "$line" | jq -r '.num_turns // "N/A"')
          TOTAL_COST=$(echo "$line" | jq -r '.total_cost_usd // "N/A"')
          IS_ERROR=$(echo "$line" | jq -r '.is_error // "N/A"')
          SESSION_ID=$(echo "$line" | jq -r '.session_id // "N/A"')
          
          echo "🏁 RESULT $TIMESTAMP:"
          echo "   └── 📊 SUBTYPE: $SUBTYPE"
          echo "   └── ⏱️ DURATION_MS: $DURATION"
          echo "   └── 🔄 NUM_TURNS: $NUM_TURNS"
          echo "   └── 💰 TOTAL_COST_USD: $TOTAL_COST"
          echo "   └── ⚠️ IS_ERROR: $IS_ERROR"
          echo "   └── 🆔 SESSION_ID: $SESSION_ID"
          
          # RESULTが来たら必ず終了（成功・エラー問わず）
          if [ "$SUBTYPE" = "error_max_turns" ]; then
            echo "⚠️ Claude Code SDK reached max turns limit, terminating..."
            echo "🏁 CCSDK_COMPLETION_DETECTED: error_max_turns"
          elif [ "$SUBTYPE" = "success" ]; then
            echo "✅ Claude Code SDK completed successfully, terminating..."
            echo "🏁 CCSDK_COMPLETION_DETECTED: success"
          else
            echo "🏁 Claude Code SDK completed with status: $SUBTYPE, terminating..."
            echo "🏁 CCSDK_COMPLETION_DETECTED: $SUBTYPE"
          fi
          
          break
          ;;
        
        *)
          # 未知のメッセージタイプの場合、全フィールドを出力
          echo "❓ UNKNOWN_$MESSAGE_TYPE $TIMESTAMP:"
          echo "$line" | jq -r 'to_entries[] | "   └── \(.key): \(.value)"'
          ;;
      esac
    else
      # JSON以外の行はそのまま表示
      echo "📄 RAW_OUTPUT $TIMESTAMP: $line"
      
      # 特別マーカー検知
      if echo "$line" | grep -q "✅.*Complete\|===WORKFLOW.*COMPLETE===\|===TASK_FINISHED.*===\|===WORKFLOW_STEP1_COMPLETE===\|===WORKFLOW_STEP2_COMPLETE==="; then
        echo "🏁 CCSDK_COMPLETION_DETECTED: special_marker"
        break
      fi
    fi
  done