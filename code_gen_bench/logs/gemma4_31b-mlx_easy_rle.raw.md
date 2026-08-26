```python
def rle_encode(s: str) -> str:
    """文字列を連続文字数+文字の形式に圧縮する"""
    if not s:
        return ""
    
    res = []
    count = 1
    # 文字列を走査して連続数をカウント
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            res.append(f"{count}{s[i - 1]}")
            count = 1
    
    # 最後の文字グループを追加
    res.append(f"{count}{s[-1]}")
    return "".join(res)

def rle_decode(s: str) -> str:
    """rle_encode の逆変換を行う"""
    if not s:
        return ""
    
    res = []
    num_str = ""
    # 文字列を走査して数字と文字を分解
    for char in s:
        if char.isdigit():
            num_str += char
        else:
            # 数字部分を整数に変換して文字を繰り返し
            res.append(char * int(num_str))
            num_str = ""
            
    return "".join(res)

if __name__ == "__main__":
    # テストケースの定義
    test_cases = [
        "",
        "a",
        "aaabbbcc",
        "abcdef",
        "a" * 20, # 2桁の数字になるケース
    ]
    
    # 個別テスト
    assert rle_encode("") == ""
    assert rle_decode("") == ""
    assert rle_encode("a") == "1a"
    assert rle_decode("1a") == "a"
    assert rle_encode("aaabbbcc") == "3a3b2c"
    assert rle_decode("3a3b2c") == "aaabbbcc"
    assert rle_encode("abcdef") == "1a1b1c1d1e1f"
    assert rle_decode("1a1b1c1d1e1f") == "abcdef"
    assert rle_encode("a" * 20) == "20a"
    assert rle_decode("20a") == "a" * 20

    # 往復テスト (rle_decode(rle_encode(s)) == s)
    for s in test_cases:
        assert rle_decode(rle_encode(s)) == s
        
    print("OK")
```