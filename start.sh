#!/bin/bash
# ローカルLLM（Ollama）でClaude Codeを起動するスクリプト

# 使用するモデル（引数で上書き可能）
MODEL="${1:-qwen2.5:1.5b}"

# Ollamaサーバーの起動確認
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "[INFO] Ollamaサーバーを起動します..."
    ollama serve &>/dev/null &
    sleep 2
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        echo "[ERROR] Ollamaサーバーの起動に失敗しました。手動で 'ollama serve' を実行してください。"
        exit 1
    fi
    echo "[OK] Ollamaサーバー 起動完了"
else
    echo "[OK] Ollamaサーバー 起動中"
fi

# モデルの存在確認
if ! ollama list 2>/dev/null | grep -q "${MODEL%%:*}"; then
    echo "[ERROR] モデル '$MODEL' が見つかりません。"
    echo "ダウンロード済みモデル:"
    ollama list
    exit 1
fi

# OllamaのAPIに向ける
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama

MCP_CONFIG="$(dirname "$0")/mcp-jma-only.json"

echo "[OK] モデル: $MODEL"
echo "[OK] 接続先: $ANTHROPIC_BASE_URL"
echo "[OK] --strict-mcp-config(jmaのみ) + ツール限定 でコンテキスト削減（CLAUDE.mdは読み込む）"
echo ""

# Claude Codeを起動
# CLAUDE.mdは読み込ませる（コーディング規約・ドキュメント更新ルール等の継続性のため）
# --strict-mcp-config + --mcp-config: MCPはjmaサーバーのみ読み込み、
#   Gmail/Calendar/Drive等の重いMCPツール一覧は除外
# --tools: Agent/Artifact等、説明文が長大なツールを除外し、基本ループ(読み書き・実行)
#          ＋調べ物(WebSearch/WebFetch)＋進捗管理(TodoWrite)だけに絞る
claude --model "$MODEL" --strict-mcp-config --mcp-config "$MCP_CONFIG" \
    --tools Bash,Edit,Write,Read,WebSearch,WebFetch,TodoWrite
