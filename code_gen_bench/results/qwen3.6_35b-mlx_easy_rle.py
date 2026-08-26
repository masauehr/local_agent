def rle_encode(s: str) -> str:
    """文字列を連続文字数+文字の形式に圧縮する"""
    if not s:
        return ""

    result = []
    current_char = s[0]
    count = 1

    for char in s[1:]:
        if char == current_char:
            count += 1
        else:
            result.append(f"{count}{current_char}")
            current_char = char
            count = 1
    result.append(f"{count}{current_char}")
    return "".join(result)

def rle_decode(s: str) -> str:
    """圧縮された文字列を元に戻す"""
    if not s:
        return ""

    result = []
    i = 0
    n = len(s)
    while i < n:
        j = i
        # 数字部分をスキャンして連番を取得
        while j < n and s[j].isdigit():
            j += 1
        count = int(s[i:j])
        char = s[j]
        result.append(char * count)
        i = j + 1
    return "".join(result)

if __name__ == "__main__":
    # テストケース: 空文字列
    assert rle_encode("") == ""
    assert rle_decode("") == ""

    # テストケース: "a"
    assert rle_encode("a") == "1a"
    assert rle_decode("1a") == "a"

    # テストケース: "aaabbbcc"
    assert rle_encode("aaabbbcc") == "3a3b2c"
    assert rle_decode("3a3b2c") == "aaabbbcc"

    # テストケース: "abcdef"（連続なし）
    assert rle_encode("abcdef") == "1a1b1c1d1e1f"

    # テストケース: 15文字以上同じ文字が連続するケース
    long_str = "a" * 16
    assert rle_encode(long_str) == "16a"
    assert rle_decode("16a") == long_str

    # 往復テスト（rle_decode(rle_encode(s)) == s が成り立つことを確認）
    round_trip_cases = ["", "x", "abc", "aaabbbcc", "abcdef", "z" * 20]
    for case in round_trip_cases:
        assert rle_decode(rle_encode(case)) == case

    print("OK")
