```python
import string


def rle_encode(s: str) -> str:
    """文字列をランレングス圧縮する（例: "aaabbbcc" -> "3a3b2c"）"""
    if not s:
        return ""

    result = []
    count = 1

    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result.append(f"{count}{s[i - 1]}")
            count = 1
    # 最後の連続文字列を追加
    result.append(f"{count}{s[-1]}")

    return "".join(result)


def rle_decode(s: str) -> str:
    """ランレングス圧縮された文字列を復元する（例: "3a3b2c" -> "aaabbbcc"）"""
    if not s:
        return ""

    result = []
    i = 0

    while i < len(s):
        # 数字部分（1桁以上）を読む
        num_str = ""
        while i < len(s) and s[i].isdigit():
            num_str += s[i]
            i += 1
        count = int(num_str)

        # 文字部分（1文字）を読む
        if i < len(s):
            result.append(s[i] * count)
            i += 1

    return "".join(result)


if __name__ == "__main__":
    # 空文字列
    assert rle_encode("") == ""
    assert rle_decode("") == ""

    # 1文字
    assert rle_encode("a") == "1a"
    assert rle_decode("1a") == "a"

    # 基本的な圧縮/復元
    assert rle_encode("aaabbbcc") == "3a3b2c"
    assert rle_decode("3a3b2c") == "aaabbbcc"

    # 連続なし（全て1文字）
    assert rle_encode("abcdef") == "1a1b1c1d1e1f"
    assert rle_decode("1a1b1c1d1e1f") == "abcdef"

    # 2桁以上の連続数（15文字の"a" → "15a"）
    s_long = "a" * 15
    assert rle_encode(s_long) == "15a"
    assert rle_decode("15a") == s_long

    # 往復テスト: 様々な文字列で rle_decode(rle_encode(s)) == s を確認
    test_cases = [
        "",
        "a",
        "ab",
        "aaabbbcc",
        "abcdef",
        "a" * 15,
        "aabbbccccdddd",
        "zyxwvutsrqponmlkjihgfedcba",
        "a" * 100,
        "ab" * 50,
        "aaabbbcccddddde",
    ]
    for s in test_cases:
        encoded = rle_encode(s)
        decoded = rle_decode(encoded)
        assert decoded == s, f"往復テスト失敗: {s!r} -> {encoded!r} -> {decoded!r}"

    print("OK")
```