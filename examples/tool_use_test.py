"""
tool_use_test.py — ローカルLLMのツール呼び出し（Function Calling）動作確認
qwen2.5-coder系モデルはツール呼び出しに対応している。
"""

import os
import json
import math
from openai import OpenAI

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

# 利用可能なツール定義
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "数式を計算して結果を返す",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "計算する数式（例: '2 + 3 * 4', 'sqrt(16)'）",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_dummy",
            "description": "指定した都市の天気情報を返す（ダミーデータ）",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "都市名（例: '東京', '大阪'）",
                    }
                },
                "required": ["city"],
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """ツールを実行して結果を文字列で返す。"""
    if name == "calculate":
        expr = args.get("expression", "")
        try:
            # 安全な計算（evalの代わりにmathモジュールを使用）
            allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            allowed["abs"] = abs
            result = eval(expr, {"__builtins__": {}}, allowed)  # noqa: S307
            return str(result)
        except Exception as e:
            return f"計算エラー: {e}"

    if name == "get_weather_dummy":
        city = args.get("city", "不明")
        # ダミーデータを返す（実際のAPI呼び出しは行わない）
        return json.dumps({"city": city, "weather": "晴れ", "temp": "22°C", "note": "ダミーデータ"}, ensure_ascii=False)

    return f"未知のツール: {name}"


def run_agent(user_message: str) -> None:
    """
    ツール呼び出しを使ったシンプルなエージェントループを実行する。
    """
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    messages = [{"role": "user", "content": user_message}]

    print(f"[ユーザー] {user_message}")

    for step in range(5):  # 最大5ステップで打ち切り
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            timeout=120,
        )

        choice = response.choices[0]
        msg = choice.message

        # ツール呼び出しがある場合
        if msg.tool_calls:
            messages.append(msg)  # アシスタントのメッセージを追加

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"  [ツール呼び出し] {fn_name}({fn_args})")

                result = execute_tool(fn_name, fn_args)
                print(f"  [ツール結果] {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        else:
            # ツール呼び出しなし → 最終回答
            print(f"[アシスタント] {msg.content}")
            break
    else:
        print("[警告] ステップ上限に達しました")


if __name__ == "__main__":
    print(f"モデル: {MODEL}")
    print(f"接続先: {OLLAMA_BASE_URL}")
    print("=" * 40)

    # ツール呼び出しのテスト
    test_cases = [
        "√144 と 2の10乗を計算してください。",
        "東京の今日の天気を教えてください。",
    ]

    for prompt in test_cases:
        print()
        run_agent(prompt)
        print("-" * 40)
