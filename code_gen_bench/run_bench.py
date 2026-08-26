#!/usr/bin/env python3
"""
コード生成能力比較ベンチマーク実行スクリプト

複数のローカルLLMに同一のお題（易・中・難）を投げ、生成コードをファイルに保存する。
生成後の実行検証は別スクリプト（verify.py）で行う。
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from batch_call import call_llm  # noqa: E402

BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"

MODELS = [
    "ornith-1.5:35b",
    "gemma4:31b-mlx",
    "qwen3.8:27b-mlx",
    "nemotron-3.5-lightning:30b-mlx",
]

TASKS = ["easy_rle", "medium_markdown", "hard_gameoflife"]

TIMEOUT_SEC = 900  # nemotronのデコード遅延を考慮し長めに設定

CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


def safe_name(model: str) -> str:
    return model.replace(":", "_").replace("/", "_")


def extract_code(raw: str) -> str | None:
    m = CODE_BLOCK_RE.search(raw)
    if m:
        return m.group(1).strip() + "\n"
    return None


def main() -> None:
    system_prompt = (BASE_DIR / "system_prompt.txt").read_text(encoding="utf-8").strip()

    summary_lines = ["| モデル | お題 | 所要時間(秒) | コード抽出 | 出力文字数 |", "|---|---|---|---|---|"]

    for model in MODELS:
        for task in TASKS:
            prompt = (PROMPTS_DIR / f"{task}.md").read_text(encoding="utf-8").strip()
            print(f"[START] {model} / {task}", flush=True)
            t0 = time.time()
            try:
                raw = call_llm(prompt, model=model, system=system_prompt, timeout=TIMEOUT_SEC)
                elapsed = time.time() - t0
                status = "OK"
            except Exception as e:  # noqa: BLE001
                elapsed = time.time() - t0
                raw = f"[ERROR] {e}"
                status = "ERROR"

            log_path = LOGS_DIR / f"{safe_name(model)}_{task}.raw.md"
            log_path.write_text(raw, encoding="utf-8")

            code = extract_code(raw) if status == "OK" else None
            if code:
                result_path = RESULTS_DIR / f"{safe_name(model)}_{task}.py"
                result_path.write_text(code, encoding="utf-8")
                extract_status = "success"
            else:
                extract_status = "failed" if status == "OK" else status

            print(
                f"[DONE]  {model} / {task}  {elapsed:.1f}s  extract={extract_status}",
                flush=True,
            )
            summary_lines.append(
                f"| {model} | {task} | {elapsed:.1f} | {extract_status} | {len(raw)} |"
            )

    summary_path = BASE_DIR / "generation_summary.md"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"\n[ALL DONE] summary -> {summary_path}", flush=True)


if __name__ == "__main__":
    main()
