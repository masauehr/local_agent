```python
#!/usr/bin/env python3
"""簡易Markdown記法をHTMLに変換するスクリプト"""

import re


def _convert_inline(text: str) -> str:
    """一行内の太字とリンクを変換する。"""
    # 太字: **text** -> <strong>text</strong>（複数回出現も対応）
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # リンク: [表示文字](URL) -> <a href="URL">表示文字</a>
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(md: str) -> str:
    """複数行のMarkdown文字列をHTML文字列に変換する。"""
    lines = md.splitlines()
    output = []
    in_list = False  # 現在リスト中のフラグ

    for line in lines:
        stripped = line.strip()

        # 空行は無視（ただしリストを閉じる）
        if not stripped:
            if in_list:
                output.append("</ul>")
                in_list = False
            continue

        # 見出し: 行頭の # の数に応じて <h1>〜<h6> に変換
        heading = re.match(r'^(#{1,6})\s+(.*)$', line)
        if heading:
            if in_list:
                output.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            text = _convert_inline(heading.group(2))
            output.append(f"<h{level}>{text}</h{level}>")
            continue

        # リスト: 行頭が `- ` で始まる行
        if re.match(r'^-\s+', line):
            if not in_list:
                output.append("<ul>")
                in_list = True
            item = re.sub(r'^-\s+', '', line).strip()
            text = _convert_inline(item)
            output.append(f"<li>{text}</li>")
            continue

        # これ以外は非空行なので <p> で囲む
        if in_list:
            output.append("</ul>")
            in_list = False
        text = _convert_inline(stripped)
        output.append(f"<p>{text}</p>")

    # 末尾でリストが開いている場合は閉じる
    if in_list:
        output.append("</ul>")

    return "\n".join(output)


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