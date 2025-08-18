        # Claude Code SDK with v3-style JSON stream processing
        npx @anthropic-ai/claude-code -p "$PROMPT" \
          --max-turns 40 \
          --permission-mode bypassPermissions \
          --verbose \
          --output-format stream-json \
          2>&1 | while IFS= read -r line; do
            # JSON形式のログを解析して見やすく表示
            if echo "$line" | jq -e 'type == "object"' > /dev/null 2>&1; then
              MESSAGE_TYPE=$(echo "$line" | jq -r '.type // "unknown"')
              
              case "$MESSAGE_TYPE" in
                "system")
                  SUBTYPE=$(echo "$line" | jq -r '.subtype // "unknown"')
                  if [ "$SUBTYPE" = "init" ]; then
                    SESSION_ID=$(echo "$line" | jq -r '.session_id')
                    echo "🎯 tools-definitions 🚀 [$(date '+%H:%M:%S')]:"
                    echo "   └── 🆔 $SESSION_ID"
                  fi
                  ;;
                "assistant")
                  CONTENT_TYPE=$(echo "$line" | jq -r '.message.content[0].type // "unknown"')
                  
                  if [ "$CONTENT_TYPE" = "text" ]; then
                    TEXT_CONTENT=$(echo "$line" | jq -r '.message.content[0].text')
                    USAGE_INPUT=$(echo "$line" | jq -r '.message.usage.input_tokens // 0')
                    USAGE_OUTPUT=$(echo "$line" | jq -r '.message.usage.output_tokens // 0')
                    
                    echo "🤖 tools-definitions 💬 [$(date '+%H:%M:%S')]:"
                    echo "   └── 📝 $TEXT_CONTENT"
                    echo "   └── 🪙 ⬇️$USAGE_INPUT ⬆️$USAGE_OUTPUT"
                    
                  elif [ "$CONTENT_TYPE" = "tool_use" ]; then
                    TOOL_NAME=$(echo "$line" | jq -r '.message.content[0].name')
                    echo "⚡ tools-definitions 🔧 [$(date '+%H:%M:%S')]:"
                    echo "   └── 🛠️ $TOOL_NAME"
                  fi
                  ;;
                "user")
                  CONTENT_TYPE=$(echo "$line" | jq -r '.message.content[0].type // "unknown"')
                  
                  if [ "$CONTENT_TYPE" = "tool_result" ]; then
                    TOOL_USE_ID=$(echo "$line" | jq -r '.message.content[0].tool_use_id')
                    IS_ERROR=$(echo "$line" | jq -r '.message.content[0].is_error // false')
                    
                    if [ "$IS_ERROR" = "true" ]; then
                      echo "❌ tools-definitions 💥 [$(date '+%H:%M:%S')]:"
                    else
                      echo "✅ tools-definitions 📋 [$(date '+%H:%M:%S')]:"
                    fi
                    echo "   └── 🆔 $TOOL_USE_ID"
                  fi
                  ;;
                "result")
                  DURATION=$(echo "$line" | jq -r '.duration_ms')
                  NUM_TURNS=$(echo "$line" | jq -r '.num_turns')
                  TOTAL_COST=$(echo "$line" | jq -r '.total_cost_usd')
                  IS_ERROR=$(echo "$line" | jq -r '.is_error')
                  
                  echo "🏁 tools-definitions 🎉 [$(date '+%H:%M:%S')]:"
                  echo "   └── ⏱️ ${DURATION}ms"
                  echo "   └── 🔄 $NUM_TURNS"
                  echo "   └── 💰 \${TOTAL_COST}"
                  echo "   └── ⚠️ $IS_ERROR"
                  ;;
              esac
            else
              # JSON以外の行はそのまま表示
              echo "$line"
            fi
          done