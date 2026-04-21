"""
agent.py — ローカルLLMを使ったインタラクティブAIエージェント
会話履歴を保持しながら対話する。Ctrl+C または 'exit' で終了。

使い方:
    python agent.py [--skill スキル名] [--list-skills]
例:
    python agent.py --skill tech_writing_ja
    python agent.py --list-skills
"""

import argparse
import os
import re
import subprocess
import sys
import json
import math
from openai import OpenAI

# 設定（環境変数で上書き可能）
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:e2b")
DEFAULT_SYSTEM_PROMPT = os.environ.get(
    "AGENT_SYSTEM_PROMPT",
    "あなたはファイル操作とgit操作ができるプログラミングアシスタントです。\n"
    "\n"
    "【必須ルール】\n"
    "- 必ず日本語のみで回答すること。中国語・その他の言語を混入させないこと。\n"
    "- ファイルの読み込み・書き込み・一覧取得・git操作が必要な場合は、"
    "自分で推測せず必ずツールを呼び出して実行すること。\n"
    "- 'git statusを確認して' → run_git ツールを args=[\"status\"] で呼び出す。\n"
    "- 'ファイルを読んで' → read_file ツールを呼び出す。\n"
    "- 'ファイルを作って' → write_file ツールを呼び出す。\n"
    "- 'コミットして' → run_git を args=[\"add\",\".\"] → args=[\"commit\",\"-m\",\"...\"] の順で呼び出す。\n"
    "- ツールの実行結果をもとに日本語で回答すること。\n",
)

# gitで許可するサブコマンド
_GIT_ALLOWED = {"status", "add", "commit", "push", "diff", "log", "show"}

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
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "カレントディレクトリ内のファイルにテキストを書き込む（新規作成・上書き）",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "書き込み先ファイルパス（相対パス）"},
                    "content": {"type": "string", "description": "書き込む内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "ディレクトリ内のファイル・フォルダ一覧を返す",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "一覧を取得するディレクトリパス（省略時はカレント）"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_git",
            "description": (
                "gitコマンドを実行する。"
                f"許可されるサブコマンド: {', '.join(sorted(_GIT_ALLOWED))}"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "gitに渡す引数リスト（例: [\"commit\", \"-m\", \"fix: typo\"]）",
                    }
                },
                "required": ["args"],
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
        abs_path = os.path.realpath(path)
        cwd = os.path.realpath(".")
        if not abs_path.startswith(cwd):
            return "エラー: カレントディレクトリ外のファイルは読めません"
        try:
            with open(abs_path, encoding="utf-8") as f:
                content = f.read()
            if len(content) > 2000:
                content = content[:2000] + "\n... (以下省略)"
            return content
        except FileNotFoundError:
            return f"エラー: ファイルが見つかりません: {path}"
        except Exception as e:
            return f"エラー: {e}"

    if name == "write_file":
        path = args.get("path", "")
        content = args.get("content", "")
        abs_path = os.path.realpath(path)
        cwd = os.path.realpath(".")
        if not abs_path.startswith(cwd):
            return "エラー: カレントディレクトリ外への書き込みはできません"
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"書き込み完了: {path} ({len(content)} 文字)"
        except Exception as e:
            return f"エラー: {e}"

    if name == "list_files":
        path = args.get("path", ".")
        abs_path = os.path.realpath(path)
        cwd = os.path.realpath(".")
        if not abs_path.startswith(cwd):
            return "エラー: カレントディレクトリ外は参照できません"
        try:
            entries = sorted(os.listdir(abs_path))
            lines = []
            for entry in entries:
                full = os.path.join(abs_path, entry)
                lines.append(f"{'[DIR] ' if os.path.isdir(full) else '      '}{entry}")
            return "\n".join(lines) if lines else "（空のディレクトリ）"
        except FileNotFoundError:
            return f"エラー: ディレクトリが見つかりません: {path}"
        except Exception as e:
            return f"エラー: {e}"

    if name == "run_git":
        git_args = args.get("args", [])
        if not git_args:
            return "エラー: git引数が空です"
        subcmd = git_args[0]
        if subcmd not in _GIT_ALLOWED:
            return f"エラー: '{subcmd}' は許可されていません。許可コマンド: {', '.join(sorted(_GIT_ALLOWED))}"
        try:
            result = subprocess.run(
                ["git"] + git_args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            return output.strip() or "（出力なし）"
        except subprocess.TimeoutExpired:
            return "エラー: タイムアウト（30秒）"
        except Exception as e:
            return f"エラー: {e}"

    return f"未知のツール: {name}"


_TOOL_CALL_RE = re.compile(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', re.DOTALL)


def _parse_text_tool_calls(content: str) -> list[dict]:
    """<tool_call> タグ形式のテキスト出力からツール呼び出しをパースする"""
    results = []
    for m in _TOOL_CALL_RE.finditer(content):
        try:
            data = json.loads(m.group(1))
            if "name" in data:
                results.append(data)
        except json.JSONDecodeError:
            pass
    return results


def run_turn(client: OpenAI, messages: list) -> str:
    """
    1ターン分の処理（ツール呼び出しを含むループ）を実行し、最終回答を返す。
    モデルが API 形式・テキスト形式どちらでツール呼び出しを出力しても対応する。
    """
    for _ in range(5):  # ツール呼び出しの最大連鎖回数
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # "required" にするとツール強制だが雑談にも適用されるため auto を維持
            timeout=120,
        )

        choice = response.choices[0]
        msg = choice.message

        if os.environ.get("AGENT_DEBUG"):
            print(f"  \033[90m[DEBUG] tool_calls={msg.tool_calls} content={repr(msg.content)}\033[0m")

        # --- パターン1: API 標準のツール呼び出し ---
        if msg.tool_calls:
            # ツール呼び出し時のノイズ content は履歴に含めない
            msg.content = None
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
            continue

        # --- パターン2: <tool_call> テキスト形式（qwen2.5 等） ---
        text_calls = _parse_text_tool_calls(msg.content or "")
        if text_calls:
            messages.append({"role": "assistant", "content": msg.content})
            tool_results = []
            for call in text_calls:
                fn_name = call["name"]
                fn_args = call.get("arguments", {})
                print(f"  \033[33m[ツール] {fn_name}({json.dumps(fn_args, ensure_ascii=False)})\033[0m")
                result = execute_tool(fn_name, fn_args)
                tool_results.append(f"ツール '{fn_name}' の実行結果:\n{result}")
            messages.append({
                "role": "user",
                "content": "\n\n".join(tool_results) + "\n\n上記の結果を使って、日本語で回答してください。",
            })
            continue

        # --- 通常の回答 ---
        return msg.content or ""

    return "（ステップ上限に達しました）"


def main() -> None:
    parser = argparse.ArgumentParser(description="ローカルLLMエージェント")
    parser.add_argument("--skill", help="読み込むスキル名（skills/配下の.mdファイル名）")
    parser.add_argument("--list-skills", action="store_true", help="利用可能なスキル一覧を表示して終了")
    args = parser.parse_args()

    # --list-skills
    if args.list_skills:
        from skill_loader import list_skills
        skills = list_skills()
        print("利用可能なスキル:", skills if skills else "（なし）")
        sys.exit(0)

    # スキル読み込み（--skill フラグ → 環境変数 → デフォルト の順で優先）
    skill_name = args.skill or os.environ.get("AGENT_SKILL")
    system_prompt = DEFAULT_SYSTEM_PROMPT
    if skill_name:
        try:
            from skill_loader import load_skill
            system_prompt = load_skill(skill_name)
            print(f"\033[35m[スキル]\033[0m '{skill_name}' を読み込みました")
        except FileNotFoundError as e:
            print(f"\033[31m[警告]\033[0m {e}")
            print("デフォルトのシステムプロンプトで続行します")

    print(f"\033[36m=== local_agent ===\033[0m")
    print(f"モデル : {MODEL}")
    print(f"接続先 : {OLLAMA_BASE_URL}")
    print(f"スキル : {skill_name or 'なし（デフォルト）'}")
    print("'exit' または Ctrl+C で終了\n")

    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    messages = [{"role": "system", "content": system_prompt}]

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
