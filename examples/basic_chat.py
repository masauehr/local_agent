"""
basic_chat.py — Ollamaとの基本的なチャット動作確認
OpenAI互換APIを使ってローカルLLMに問い合わせる最小サンプル。
"""

import os
from openai import OpenAI

# 接続先（環境変数で上書き可能）
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")


def chat(prompt: str, system: str = "あなたは親切なAIアシスタントです。日本語で答えてください。") -> str:
    """
    ローカルLLMに1回問い合わせて回答を返す。
    """
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama",  # ダミー値（Ollamaは認証不要）
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        timeout=120,  # ローカルLLMは遅いので長めに設定
    )

    return response.choices[0].message.content


def chat_stream(prompt: str, system: str = "あなたは親切なAIアシスタントです。日本語で答えてください。") -> None:
    """
    ストリーミングで回答を逐次出力する。
    """
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama",
    )

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        timeout=120,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print()  # 改行


if __name__ == "__main__":
    print(f"モデル: {MODEL}")
    print(f"接続先: {OLLAMA_BASE_URL}")
    print("-" * 40)

    # 動作確認用プロンプト
    test_prompts = [
        "Pythonでフィボナッチ数列を生成する関数を書いてください。",
        "バブルソートのアルゴリズムを簡潔に説明してください。",
    ]

    for prompt in test_prompts:
        print(f"\n[質問] {prompt}")
        print("[回答] ", end="")
        chat_stream(prompt)
        print()
