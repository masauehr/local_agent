#!/usr/bin/env python3
"""
生成コードの実行検証スクリプト

results/ 配下の各 .py を実際にサブプロセスで実行し、
・正常終了するか（exit code）
・お題ごとの期待する出力パターンが含まれるか
を確認してレポートを作る。
"""
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

MODELS = [
    "ornith-1.5:35b",
    "gemma4:31b-mlx",
    "qwen3.6:35b-mlx",
    "qwen3.8:27b-mlx",
    "nemotron-3.5-lightning:30b-mlx",
]

TASKS = ["easy_rle", "medium_markdown", "hard_gameoflife"]

RUN_TIMEOUT = 15  # 秒


def safe_name(model: str) -> str:
    return model.replace(":", "_").replace("/", "_")


def check_easy(stdout: str) -> tuple[bool, str]:
    if "OK" in stdout:
        return True, "OKを出力"
    return False, "OKが出力されなかった（assert失敗 or 未実装）"


def check_medium(stdout: str) -> tuple[bool, str]:
    required = ["<h1>", "<h2>", "<strong>", "<ul>", "<li>", "<a href="]
    missing = [tag for tag in required if tag not in stdout]
    if not missing:
        return True, "必須タグを全て出力"
    return False, f"欠落タグ: {', '.join(missing)}"


def check_hard(stdout: str) -> tuple[bool, str]:
    gen_count = len(re.findall(r"Generation\s*[0-4]\b", stdout))
    has_glyph = "#" in stdout and "." in stdout
    if gen_count >= 5 and has_glyph:
        return True, f"Generation表記{gen_count}件・グリフ出力あり"
    return False, f"Generation表記{gen_count}件（5件必要）・グリフ出力={has_glyph}"


CHECKERS = {
    "easy_rle": check_easy,
    "medium_markdown": check_medium,
    "hard_gameoflife": check_hard,
}


def main() -> None:
    rows = ["| モデル | お題 | ファイル存在 | 実行結果 | 判定 | 備考 |", "|---|---|---|---|---|---|"]

    for model in MODELS:
        for task in TASKS:
            path = RESULTS_DIR / f"{safe_name(model)}_{task}.py"
            if not path.exists():
                rows.append(f"| {model} | {task} | なし | - | ❌ FAIL | コード抽出失敗 |")
                continue

            try:
                proc = subprocess.run(
                    [sys.executable, str(path)],
                    capture_output=True,
                    text=True,
                    timeout=RUN_TIMEOUT,
                )
                if proc.returncode != 0:
                    err_line = (proc.stderr.strip().splitlines() or ["(no stderr)"])[-1]
                    rows.append(
                        f"| {model} | {task} | あり | exit={proc.returncode} | ❌ FAIL | {err_line[:80]} |"
                    )
                    continue
                ok, note = CHECKERS[task](proc.stdout)
                mark = "✅ PASS" if ok else "❌ FAIL"
                rows.append(f"| {model} | {task} | あり | exit=0 | {mark} | {note} |")
            except subprocess.TimeoutExpired:
                rows.append(f"| {model} | {task} | あり | timeout>{RUN_TIMEOUT}s | ❌ FAIL | 無限ループ疑い |")
            except Exception as e:  # noqa: BLE001
                rows.append(f"| {model} | {task} | あり | - | ❌ FAIL | 実行例外: {e} |")

    report = "\n".join(rows) + "\n"
    (BASE_DIR / "verify_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
