#!/usr/bin/env python3
"""
バッチLLM呼び出しCLI — ローカル自動化スクリプト向け汎用ツール

Ollama の OpenAI互換エンドポイントを直接使用（ラッパーサーバー不要）。
stdin / ファイルからプロンプトを読み込み、LLM応答を stdout / ファイルへ出力する。

Usage:
    echo "こんにちは" | python3 batch_call.py
    python3 batch_call.py --prompt-file prompt.txt --output result.md
    cat prompt.txt | python3 batch_call.py --model qwen3.6:35b-mlx > result.md

他プロジェクトの launchd スクリプトからの利用例:
    RESULT=$(python3 ~/projects/local_agent/scripts/batch_call.py \\
        --model qwen3.6:27b-mlx \\
        --prompt-file prompt.txt)

環境変数:
    OLLAMA_BASE_URL   Ollama エンドポイント（デフォルト: http://localhost:11434）
    BATCH_LLM_MODEL   使用モデル（デフォルト: qwen3.6:27b-mlx）
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("BATCH_LLM_MODEL", "qwen3.6:27b-mlx")
ENDPOINT = f"{OLLAMA_BASE_URL}/v1/chat/completions"


def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    timeout: int = 600,
) -> str:
    """ローカルLLMにプロンプトを送り、テキスト応答を返す。"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps({
        "model": model,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())

    return data["choices"][0]["message"]["content"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ローカルLLMへのバッチ呼び出しCLI（Ollama OpenAI互換エンドポイント直接使用）",
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"使用するモデル名（デフォルト: {DEFAULT_MODEL}）",
    )
    parser.add_argument(
        "--prompt-file", "-p",
        help="プロンプトを読み込むファイルパス（省略時は stdin から読む）",
    )
    parser.add_argument(
        "--output", "-o",
        help="出力先ファイルパス（省略時は stdout へ出力）",
    )
    parser.add_argument(
        "--system", "-s",
        help="システムプロンプト文字列",
    )
    parser.add_argument(
        "--system-file",
        help="システムプロンプトを読み込むファイルパス（--system より優先）",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=600,
        help="タイムアウト秒数（デフォルト: 600）",
    )
    args = parser.parse_args()

    # プロンプト読み込み
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        print("[ERROR] プロンプトを stdin か --prompt-file で渡してください", file=sys.stderr)
        sys.exit(1)

    if not prompt:
        print("[ERROR] プロンプトが空です", file=sys.stderr)
        sys.exit(1)

    # システムプロンプト
    system = None
    if args.system_file:
        system = Path(args.system_file).read_text(encoding="utf-8").strip()
    elif args.system:
        system = args.system

    # LLM 呼び出し
    try:
        result = call_llm(prompt, model=args.model, system=system, timeout=args.timeout)
    except urllib.error.URLError as e:
        print(f"[ERROR] Ollama 接続失敗: {e}", file=sys.stderr)
        print("  Ollama が起動しているか確認: ollama serve", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"[ERROR] レスポンス解析失敗: {e}", file=sys.stderr)
        sys.exit(1)

    # 出力
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"[OK] 出力: {args.output} ({len(result)} 文字)", file=sys.stderr)
    else:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
