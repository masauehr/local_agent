```python
import re


def markdown_to_html(md: str) -> str:
    """簡易Markdown文字列をHTML文字列に変換する。"""
    lines = md.splitlines()
    result: list[str] = []
    i = 0

    # インライン処理: リンク → 太字
    def apply_inline(text: str) -> str:
        # リンク [表示文字](URL) → <a href="URL">表示文字</a>
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # 太字 **text** → <strong>text</strong>
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        return text

    while i < len(lines):
        line = lines[i]

        # 空行は無視
        if not line.strip():
            i += 1
            continue

        # 見出し: 行頭の # 1〜6個 + 空白 + 本文
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = apply_inline(heading_match.group(2))
            result.append(f'<h{level}>{content}</h{level}>')
            i += 1
            continue

        # リスト: 連続する "- " 行をまとめて <ul> で囲む
        if line.startswith('- '):
            result.append('<ul>')
            while i < len(lines) and lines[i].startswith('- '):
                item = apply_inline(lines[i][2:])
                result.append(f'<li>{item}</li>')
                i += 1
            result.append('</ul>')
            continue

        # その他非空行 → <p>...</p>
        content = apply_inline(line)
        result.append(f'<p>{content}</p>')
        i += 1

    return '\n'.join(result)


if __name__ == "__main__":
    sample = """# 見出し1
## 見出し2

これは**太字**を含む段落です。

- リスト項目1
- リスト項目2
- リスト項目3

詳しくは[公式サイト](https://example.com)を参照してください。"""

    print(markdown_to_html(sample))
```