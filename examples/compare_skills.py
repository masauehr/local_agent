"""
compare_skills.py — スキルあり・なしで同じ質問の回答を比較する実験スクリプト

使い方:
    python examples/compare_skills.py <モデル名> <スキル名> <質問>
例:
    python examples/compare_skills.py qwen2.5:7b tech_writing_ja 量子コンピュータを初心者向けに説明して
"""
import os
import sys
from pathlib import Path

# scripts/ のskill_loaderをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from skill_loader import load_skill

from openai import OpenAI

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")


def ask(client: OpenAI, model: str, question: str, system_prompt: str | None = None) -> str:
    """モデルに質問して回答を返す（ストリーミングなし）"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        timeout=120,
    )
    return response.choices[0].message.content or ""


def compare(model: str, skill_name: str, question: str) -> None:
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    skill = load_skill(skill_name)

    print("=" * 60)
    print(f"モデル : {model}")
    print(f"スキル : {skill_name}")
    print(f"質問  : {question}")
    print("=" * 60)

    print("\n\033[33m【スキルなし】\033[0m")
    print(ask(client, model, question))

    print("\n" + "-" * 60)
    print(f"\n\033[36m【スキルあり: {skill_name}】\033[0m")
    print(ask(client, model, question, skill))

    print("\n" + "=" * 60)


def main() -> None:
    if len(sys.argv) < 4:
        print("使い方: python examples/compare_skills.py <モデル名> <スキル名> <質問>")
        print("例: python examples/compare_skills.py qwen2.5:7b tech_writing_ja 量子コンピュータを説明して")
        sys.exit(1)

    model = sys.argv[1]
    skill_name = sys.argv[2]
    question = " ".join(sys.argv[3:])
    compare(model, skill_name, question)


if __name__ == "__main__":
    main()
