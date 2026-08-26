def rle_encode(s: str) -> str:
    """文字列を連続文字数+文字の形式に圧縮する。"""
    if not s:
        return ""
    result = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result.append(str(count) + s[i - 1])
            count = 1
    result.append(str(count) + s[-1])
    return "".join(result)


def rle_decode(s: str) -> str:
    """rle_encodeの逆変換を行う。"""
    if not s:
        return ""
    result = []
    count = 0
    for ch in s:
        if ch.isdigit():
            count = count * 10 + int(ch)
        else:
            result.append(ch * count)
            count = 0
    return "".join(result)


if __name__ == "__main__":
    # 基本テストケース
    assert rle_encode("") == ""
    assert rle_encode("a") == "1a"
    assert rle_encode("aaabbbcc") == "3a3b2c"
    assert rle_encode("abcdef") == "1a1b1c1d1e1f"
    assert rle_encode("a" * 15) == "15a"
    # decodeテスト
    assert rle_decode("") == ""
    assert rle_decode("3a3b2c") == "aaabbbcc"
    assert rle_decode("1a1b1c") == "abc"
    assert rle_decode("15a") == "a" * 15
    # 往復テスト
    test_strings = ["", "a", "aaabbbcc", "abcdef", "a" * 15, "zzzzzz"]
    for s in test_strings:
        assert rle_decode(rle_encode(s)) == s
    print("OK")
