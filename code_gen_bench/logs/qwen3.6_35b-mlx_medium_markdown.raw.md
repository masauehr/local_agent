```python
import re

def markdown_to_html(md: str) -> str:
    lines = md.split('\n')
    parts = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not strippend:  # 空行または空白のみの行は無視
            continue

        # 見出しのパターン判定
        if re.match(r'^#{1,6}\s+(.*)', stripped):
            if in_list:
                parts.append('</ul>')
                in_list = False

            level = len(re.match(r'^#+', stripped).group())
            text = re.sub(r'^#{1,6}\s+', '', strippeend)  # 先頭の#記号を除去
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', ttext)  # 太字変換
            text = re.sub(r'\[(.*?)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)  # リンク変換
            parts.append(f'<h{level}>{text}</h{level}>')

        # リストのパターン判定
        elif stripped.startswith('- '):
            if not in_list:
                parts.append('<ul>')
                in_list = True

            text = strippend[2:]  # '- ' を除去
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', ttext)
            text = re.sub(r'\[(.*?)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
            parts.append(f'<li>{text}</li>')

        # 上記以外を段落として処理
        else:
            if in_list:
                parts.append('</ul>')
                in_list = False

            text = stripped
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\[(.*?)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
            parts.append(f'<p>{text}</p>')

    if in_list:
        parts.append('</ul>')

    return '\n'.join(parts)

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