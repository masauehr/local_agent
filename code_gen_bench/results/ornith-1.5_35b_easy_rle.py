import re


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
            result += f"{count}{s[i - 1]}"
            count = 1
    result += f"{count}{s[-1]}"
    return result


def rle_decode(s: str) -> str:
    """rle_encode の逆変換を行う。連続数は2桁以上になる場合がある。"""
    if s == "":
        return ""
    pattern = re.compile(r"(\d+)([a-z])")
    result = ""
    for match in pattern.finditer(s):
        count = int(match.group(1))
        char = match.group(2)
        result += char * count
    return result


if __name__ == "__main__":
    test_cases = [
        "",
        "a",
        "aaabbbcc",
        "abcdef",
        "a" * 15,  # 15文字連続で2桁の数字になるケース
    ]

    for t in test_cases:
        encoded = rle_encode(t)
        # 往復テスト
        assert rle_decode(encoded) == t
        # エンコードとデコードの整合性
        assert rle_encode(rle_decode(encoded)) == encoded

    # 2桁の数字になることを明示的に確認
    assert rle_encode("a" * 15) == "15a"
    assert rle_decode("15a") == "a" * 15

    print("OK")
