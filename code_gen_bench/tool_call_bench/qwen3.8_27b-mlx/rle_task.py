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
            result.append(f"{count}{s[i - 1]}")
            count = 1
    result.append(f"{count}{s[-1]}")
    return "".join(result)


def rle_decode(s: str) -> str:
    """rle_encode の逆変換を行う。"""
    if not s:
        return ""
    result = []
    i = 0
    while i < len(s):
        # バグ: 連続数を1桁しか読まないため、2桁以上のケースで壊れる
        count = int(s[i])
        char = s[i + 1]
        result.append(char * count)
        i += 2
    return "".join(result)


if __name__ == "__main__":
    assert rle_encode("") == ""
    assert rle_decode("") == ""
    assert rle_encode("a") == "1a"
    assert rle_decode("1a") == "a"
    assert rle_encode("aaabbbcc") == "3a3b2c"
    assert rle_decode("3a3b2c") == "aaabbbcc"
    assert rle_encode("abcdef") == "1a1b1c1d1e1f"
    assert rle_decode("1a1b1c1d1e1f") == "abcdef"
    # 15文字連続（2桁の数字になるケース）
    assert rle_encode("a" * 15) == "15a"
    assert rle_decode("15a") == "a" * 15
    for s in ["", "a", "aaabbbcc", "abcdef", "a" * 15, "a" * 100]:
        assert rle_decode(rle_encode(s)) == s
    print("OK")
