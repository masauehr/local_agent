```python
def rle_encode(s: str) -> str:
    """文字列を連続文字数+文字の形式に圧縮する。"""
    if s == "":
        return ""
    result = ""
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result += str(count) + s[i - 1]
            count = 1
    result += str(count) + s[-1]
    return result


def rle_decode(s: str) -> str:
    """rle_encodeの逆変換を行う（連続数は1桁以上任意の桁数に対応）。"""
    if s == "":
        return ""
    result = ""
    i = 0
    while i < len(s):
        number = ""
        # 数字部分を読み取る（1桁以上）
        while i < len(s) and s[i].isdigit():
            number += s[i]
            i += 1
        # その直後の1文字を読み取る
        char = s[i]
        i += 1
        result += char * int(number)
    return result


if __name__ == "__main__":
    # 基本ケース
    for case in ["", "a", "aaabbbcc", "abcdef"]: