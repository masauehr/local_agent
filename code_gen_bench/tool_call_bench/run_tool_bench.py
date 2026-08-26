#!/usr/bin/env python3
"""
Claude Code経由でのツール呼び出し安定性テスト

各ローカルモデルに対し、独立した使い捨てgitリポジトリ内で
「バグ修正→テスト実行→git commit」という実践的なフルフローを
Claude Code (claude -p, --dangerously-skip-permissions) で実行させ、
実際にコミットされたか・修正が正しいかを検証する。
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent

MODELS = [
    "ornith-1.5:35b",
    "gemma4:31b-mlx",
    "qwen3.6:35b-mlx",
    "qwen3.8:27b-mlx",
    "nemotron-3.5-lightning:30b-mlx",
]

TASK_PROMPT = (
    "rle_task.py の rle_decode() 関数にバグがあります。"
    "連続数が2桁以上になるケース（例: 15文字連続で rle_decode(\"15a\") を呼ぶ）で正しく復元できません。"
    "原因を特定して修正し、`python3 rle_task.py` を実行してテストがすべて通ること"
    "（\"OK\"が標準出力されること）を確認してください。"
    "修正できたら `git add rle_task.py` した上で、適切な日本語のコミットメッセージで `git commit` してください。"
)

TIMEOUT_SEC = 900


def safe_name(model: str) -> str:
    return model.replace(":", "_").replace("/", "_")


def run_one(model: str) -> dict:
    repo_dir = BASE_DIR / safe_name(model)
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = "http://localhost:11434"
    env["ANTHROPIC_API_KEY"] = "ollama"

    cmd = [
        "claude",
        "-p", TASK_PROMPT,
        "--model", model,
        "--dangerously-skip-permissions",
        "--output-format", "json",
    ]

    t0 = time.time()
    result = {"model": model, "commit_made": False, "test_passes": False, "claude_exit": None, "elapsed": None, "error": None}
    try:
        proc = subprocess.run(
            cmd, cwd=repo_dir, env=env,
            capture_output=True, text=True, timeout=TIMEOUT_SEC,
        )
        result["elapsed"] = time.time() - t0
        result["claude_exit"] = proc.returncode
        (repo_dir / "claude_stdout.json").write_text(proc.stdout, encoding="utf-8")
        (repo_dir / "claude_stderr.log").write_text(proc.stderr, encoding="utf-8")

        try:
            payload = json.loads(proc.stdout)
            result["num_turns"] = payload.get("num_turns")
            result["duration_api_ms"] = payload.get("duration_api_ms")
            result["is_error"] = payload.get("is_error")
        except json.JSONDecodeError:
            result["num_turns"] = None

    except subprocess.TimeoutExpired:
        result["elapsed"] = TIMEOUT_SEC
        result["error"] = f"timeout>{TIMEOUT_SEC}s"

    # コミットが増えたか確認（initialの1件から増えているか）
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=repo_dir, capture_output=True, text=True,
    )
    commit_count = len(log.stdout.strip().splitlines())
    result["commit_count"] = commit_count
    result["commit_made"] = commit_count >= 2

    # 修正後のコードが実際に正しく動くか実行して検証
    test = subprocess.run(
        [sys.executable, "rle_task.py"], cwd=repo_dir,
        capture_output=True, text=True, timeout=20,
    )
    result["test_stdout"] = test.stdout.strip()
    result["test_passes"] = test.returncode == 0 and "OK" in test.stdout

    return result


def main() -> None:
    all_results = []
    for model in MODELS:
        print(f"[START] {model}", flush=True)
        r = run_one(model)
        all_results.append(r)
        print(
            f"[DONE]  {model}  elapsed={r['elapsed']:.1f}s  "
            f"commit={r['commit_made']}  test_pass={r['test_passes']}  "
            f"claude_exit={r['claude_exit']}  error={r['error']}",
            flush=True,
        )

    (BASE_DIR / "tool_bench_results.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n[ALL DONE] -> tool_bench_results.json", flush=True)


if __name__ == "__main__":
    main()
