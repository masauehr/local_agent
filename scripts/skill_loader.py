"""スキルファイルの読み込みユーティリティ"""
from pathlib import Path

# scripts/ の1つ上の skills/ ディレクトリを参照
SKILLS_DIR = Path(__file__).parent.parent / "skills"


def load_skill(skill_name: str) -> str:
    """.md拡張子省略可。スキルファイルをテキストとして返す。"""
    for candidate in [SKILLS_DIR / f"{skill_name}.md", SKILLS_DIR / skill_name]:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    available = list_skills()
    raise FileNotFoundError(
        f"スキル '{skill_name}' が見つかりません。利用可能: {available}"
    )


def list_skills() -> list[str]:
    """skills/ 配下の .md ファイル一覧（README除く）"""
    if not SKILLS_DIR.exists():
        return []
    return [p.stem for p in sorted(SKILLS_DIR.glob("*.md")) if p.name != "README.md"]
