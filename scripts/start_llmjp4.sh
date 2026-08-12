#!/bin/bash
# llm-jp-4 用 llama-server 起動スクリプト
# Cursor / Continue.dev のバックエンドとして使う

GGUF="$HOME/.ollama/models/blobs/sha256-ca8e85cb7cea96362beee30f500c2d810e95606dac81ec8d10fd7a1b5cc3a768"
PORT=8088
LOG="/tmp/llama-server-llmjp4.log"

# すでに起動中なら何もしない
if curl -s "http://127.0.0.1:$PORT/health" | grep -q '"ok"'; then
    echo "llm-jp-4 は起動済みです (port $PORT)"
    exit 0
fi

echo "llm-jp-4 を起動中..."
llama-server \
    -m "$GGUF" \
    --alias "llm-jp-4" \
    --jinja \
    --host 127.0.0.1 --port "$PORT" \
    -c 16384 -t 8 \
    > "$LOG" 2>&1 &

echo "PID: $! / ログ: $LOG"

# 起動待ち（最大30秒）
for i in $(seq 1 30); do
    if curl -s "http://127.0.0.1:$PORT/health" | grep -q '"ok"'; then
        echo "起動完了 → http://127.0.0.1:$PORT"
        exit 0
    fi
    sleep 1
done

echo "タイムアウト: ログを確認してください → $LOG"
exit 1
