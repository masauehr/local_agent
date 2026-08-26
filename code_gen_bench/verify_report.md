| モデル | お題 | ファイル存在 | 実行結果 | 判定 | 備考 |
|---|---|---|---|---|---|
| ornith-1.5:35b | easy_rle | あり | exit=0 | ✅ PASS | OKを出力 |
| ornith-1.5:35b | medium_markdown | あり | exit=0 | ✅ PASS | 必須タグを全て出力 |
| ornith-1.5:35b | hard_gameoflife | あり | exit=0 | ✅ PASS | Generation表記5件・グリフ出力あり |
| gemma4:31b-mlx | easy_rle | あり | exit=0 | ✅ PASS | OKを出力 |
| gemma4:31b-mlx | medium_markdown | あり | exit=0 | ✅ PASS | 必須タグを全て出力 |
| gemma4:31b-mlx | hard_gameoflife | あり | exit=0 | ✅ PASS | Generation表記5件・グリフ出力あり |
| qwen3.6:35b-mlx | easy_rle | あり | exit=0 | ✅ PASS | OKを出力 |
| qwen3.6:35b-mlx | medium_markdown | あり | exit=1 | ❌ FAIL | NameError: name 'strippend' is not defined. Did you mean: 'stripped'? |
| qwen3.6:35b-mlx | hard_gameoflife | あり | exit=0 | ✅ PASS | Generation表記5件・グリフ出力あり |
| qwen3.8:27b-mlx | easy_rle | あり | exit=0 | ✅ PASS | OKを出力 |
| qwen3.8:27b-mlx | medium_markdown | あり | exit=0 | ✅ PASS | 必須タグを全て出力 |
| qwen3.8:27b-mlx | hard_gameoflife | あり | exit=0 | ✅ PASS | Generation表記5件・グリフ出力あり |
| nemotron-3.5-lightning:30b-mlx | easy_rle | あり | exit=0 | ✅ PASS | OKを出力 |
| nemotron-3.5-lightning:30b-mlx | medium_markdown | あり | exit=0 | ✅ PASS | 必須タグを全て出力 |
| nemotron-3.5-lightning:30b-mlx | hard_gameoflife | あり | exit=0 | ✅ PASS | Generation表記5件・グリフ出力あり |
