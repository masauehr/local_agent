"""
agent.py — ローカルLLMを使ったインタラクティブAIエージェント
会話履歴を保持しながら対話する。Ctrl+C または 'exit' で終了。
"""

import os
import sys
import json
import math
from openai import OpenAI

# 設定（環境変数で上書き可能）
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
SYSTEM_PROMPT = os.environ.get(
    "AGENT_SYSTEM_PROMPT",
    "あなたは優秀なプログラミングアシスタントです。日本語で丁寧に回答してください。"
    "コードを示すときは説明も添えてください。",
)

# ツール定義
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "数式を計算して結果を返す",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "計算する数式"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "カレントディレクトリ内のテキストファイルを読み込む",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "ファイルパス（相対パス）"}
                },
                "required": ["path"],
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """ツールを実行する。"""
    if name == "calculate":
        expr = args.get("expression", "")
        try:
            allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            allowed["abs"] = abs
            result = eval(expr, {"__builtins__": {}}, allowed)  # noqa: S307
            return str(result)
        except Exception as e:
            return f"計算エラー: {e}"

    if name == "read_file":
        path = args.get("path", "")
        # パストラバーサル対策
        abs_path = os.path.realpath(path)
        cwd = os.path.realpath(".")
        if not abs_path.startswith(cwd):
            return "エラー: カレントディレクトリ外のファイルは読めません"
        try:
            with open(abs_path, encoding="utf-8") as f:
                content = f.read()
            # 長すぎる場合は先頭2000文字に制限
            if len(content) > 2000:
                content = content[:2000] + "\n... (以下省略)"
            return content
        except FileNotFoundError:
            return f"エラー: ファイルが見つかりません: {path}"
        except Exception as e:
            return f"エラー: {e}"

    return f"未知のツール: {name}"


def run_turn(client: OpenAI, messages: list) -> str:
    """
    1ターン分の処理（ツール呼び出しを含むループ）を実行し、最終回答を返す。
    """
    for _ in range(5):  # ツール呼び出しの最大連鎖回数
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            timeout=120,
        )

        choice = response.choices[0]
        msg = choice.message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"  \033[33m[ツール] {fn_name}({json.dumps(fn_args, ensure_ascii=False)})\033[0m")
                result = execute_tool(fn_name, fn_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            return msg.content or ""

    return "（ステップ上限に達しました）"


def main() -> None:
    print(f"\033[36m=== local_agent ===\033[0m")
    print(f"モデル : {MODEL}")
    print(f"接続先 : {OLLAMA_BASE_URL}")
    print("'exit' または Ctrl+C で終了\n")

    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("\033[32m[あなた]\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n終了します。")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "終了"):
            print("終了します。")
            sys.exit(0)

        messages.append({"role": "user", "content": user_input})

        try:
            answer = run_turn(client, messages)
        except Exception as e:
            print(f"\033[31m[エラー] {e}\033[0m")
            # エラーが出たメッセージを履歴から除去
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": answer})
        print(f"\033[34m[AI]\033[0m {answer}\n")


if __name__ == "__main__":
    main()
