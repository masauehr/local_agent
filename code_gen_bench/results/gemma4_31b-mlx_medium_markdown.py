import re

def markdown_to_html(md: str) -> str:
    """
    簡易Markdown記法をHTMLに変換する
    """
    lines = md.splitlines()
    html_output = []
    in_list = False

    def process_inline(text: str) -> str:
        # 太字の変換: **text** -> <strong>text</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # リンクの変換: [text](url) -> <a href="url">text</a>
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        return text

    for line in lines:
        # 空行は無視する
        if not line.strip():
            if in_list:
                html_output.append("</ul>")
                in_list = False
            continue

        # 見出しの判定 (# 1-6個)
        if line.startswith('#'):
            if in_list:
                html_output.append("</ul>")
                in_list = False
            
            level = 0
            while level < len(line) and line[level] == '#':
                level += 1
            
            if level <= 6:
                content = line[level:].strip()
                html_output.append(f"<h{level}>{process_inline(content)}</h{level}>")
                continue

        # リストの判定 (- )
        if line.startswith('- '):
            if not in_list:
                html_output.append("<ul>")
                in_list = True
            
            content = line[2:].strip()
            html_output.append(f"<li>{process_inline(content)}</li>")
            continue

        # それ以外の非空行は段落（<p>）として処理
        if in_list:
            html_output.append("</ul>")
            in_list = False
        
        html_output.append(f"<p>{process_inline(line)}</p>")

    # 最後にリストが閉じられていない場合は閉じる
    if in_list:
        html_output.append("</ul>")

    return "".join(html_output)

if __name__ == "__main__":
    sample_md = """# 見出し1
## 見出し2

これは**太字**を含む段落です。

- リスト項目1
- リスト項目2
- リスト項目3

詳しくは[公式サイト](https://example.com)を参照してください。"""

    print(markdown_to_html(sample_md))
