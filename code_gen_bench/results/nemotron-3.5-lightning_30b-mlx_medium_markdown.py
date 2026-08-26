import re


def markdown_to_html(md: str) -> str:
    lines = md.split('\n')
    result_parts = []
    list_buffer = []

    link_re = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    bold_re = re.compile(r'\*\*(.+?)\*\*')

    def flush_list():
        if list_buffer:
            result_parts.append('<ul>')
            for item in list_buffer:
                result_parts.append(f'<li>{item}</li>')
            result_parts.append('</ul>')
            list_buffer.clear()

    for line in lines:
        # リスト項目の場合
        if line.startswith('- '):
            content = line[2:].strip()
            if content:
                list_buffer.append(content)
            continue

        # それ以前のリストを閉じる
        flush_list()

        # 見出しの判定
        heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = bold_re.sub(r'<strong>\1</strong>', heading_match.group(2))
            text = link_re.sub(r'<a href="\2">\1</a>', text)
            result_parts.append(f'<h{level}>{text}</h{level}>')
            continue

        # リンクと太字の変換
        processed = link_re.sub(r'<a href="\2">\1</a>', line)
        processed = bold_re.sub(r'<strong>\1</strong>', processed)

        # 空行以外は段落で囲む
        if processed.strip():
            result_parts.append(f'<p>{processed}</p>')
        # 空行は無視（何もしない）

    # 未閉じのリストがあれば閉じる
    flush_list()

    return '\n'.join(result_parts)


if __name__ == "__main__":
    sample_md = """# 見出し1
## 見出し2

これは**太字**を含む段落です。

- リスト項目1
- リスト項目2
- リスト項目3

詳しくは[公式サイト](https://example.com)を参照してください。"""
    print(markdown_to_html(sample_md))
