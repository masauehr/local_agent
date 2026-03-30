#!/bin/bash
# Ollama + ローカルLLM セットアップスクリプト

set -e

echo "=== local_agent セットアップ ==="

# Ollamaのインストール確認
if command -v ollama &>/dev/null; then
    echo "[OK] Ollama インストール済み: $(ollama --version 2>/dev/null || echo '不明')"
else
    echo "[INFO] Ollamaをインストールします..."
    if command -v brew &>/dev/null; then
        brew install ollama
    else
        echo "[ERROR] Homebrewが見つかりません。https://ollama.com/download/mac から手動でインストールしてください。"
        exit 1
    fi
fi

# Ollamaサーバーの起動確認
if curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "[OK] Ollamaサーバー 起動中"
else
    echo "[INFO] Ollamaサーバーを起動します..."
    ollama serve &
    sleep 3
    if curl -s http://localhost:11434/api/tags &>/dev/null; then
        echo "[OK] Ollamaサーバー 起動完了"
    else
        echo "[ERROR] Ollamaサーバーの起動に失敗しました。手動で 'ollama serve' を実行してください。"
        exit 1
    fi
fi

# デフォルトモデルのダウンロード
DEFAULT_MODEL="qwen2.5:1.5b"
echo "[INFO] モデル '$DEFAULT_MODEL' を確認中..."

if ollama list 2>/dev/null | grep -q "$DEFAULT_MODEL"; then
    echo "[OK] モデル '$DEFAULT_MODEL' はダウンロード済みです"
else
    echo "[INFO] モデル '$DEFAULT_MODEL' をダウンロードします（約4.7GB）..."
    ollama pull "$DEFAULT_MODEL"
    echo "[OK] ダウンロード完了"
fi

# Python仮想環境の作成とパッケージインストール
VENV_DIR="$(dirname "$0")/../.venv"
echo "[INFO] Python仮想環境を確認中..."
if [ -d "$VENV_DIR" ]; then
    echo "[OK] .venv 既存"
else
    echo "[INFO] .venv を作成します..."
    python3 -m venv "$VENV_DIR"
fi

if "$VENV_DIR/bin/python3" -c "import openai" &>/dev/null; then
    echo "[OK] openai パッケージ インストール済み"
else
    echo "[INFO] openai パッケージをインストールします..."
    "$VENV_DIR/bin/pip" install openai
fi

echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "使い方:"
echo "  # venvを有効化（毎回必要）"
echo "  source .venv/bin/activate"
echo ""
echo "  # Ollamaサーバー起動（別ターミナルで）"
echo "  ollama serve"
echo ""
echo "  # サンプルコードを実行"
echo "  python3 examples/basic_chat.py"
echo ""
echo "  # エージェントを起動"
echo "  python3 scripts/agent.py"
echo ""
echo "  # Claude Code をローカルLLMで起動"
echo "  export ANTHROPIC_BASE_URL=http://localhost:11434"
echo "  export ANTHROPIC_API_KEY=ollama"
echo "  claude --model qwen2.5:1.5b"
