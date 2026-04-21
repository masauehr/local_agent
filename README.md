# local_agent

ローカルLLM（Ollama）を使ったAIエージェント環境。MacでClaude Code風のCLI体験をAPIコストゼロで実現する。

## 概要

- **目的**: OllamaのAnthropic互換APIを通じてローカルLLMをエージェントとして動かす
- **対象モデル**: `qwen2.5-coder:7b`（コード生成向き、4.7GB）など
- **推奨環境**: Mac (Apple Silicon)、メモリ16GB以上

## ディレクトリ構成

```
local_agent/
├── README.md           # このファイル
├── CLAUDE.md           # Claude Code向け指示
├── plan.md             # 初期構想メモ
├── setup/              # セットアップスクリプト
├── scripts/            # エージェント実行スクリプト
└── examples/           # 使用例・動作確認用コード
```

## 前提条件

| 要件 | 詳細 |
|------|------|
| OS | macOS (Apple Silicon推奨) |
| メモリ | 16GB以上（7Bモデル）、32GB以上（14B以上のモデル） |
| Ollama | v0.15以降（Anthropic互換API対応） |
| Python | 3.10以上（スクリプト実行用） |

## セットアップ手順

### 1. Ollamaのインストール

```bash
# Homebrewでインストール
brew install ollama

# またはpkg形式でインストール
# https://ollama.com/download/mac からダウンロード
```

### 2. Ollamaサーバー起動

```bash
ollama serve
```

### 3. モデルのダウンロード

```bash
# コード生成向け（推奨・4.7GB）
ollama pull qwen2.5-coder:7b

# より高精度（要高スペック・9GB）
ollama pull qwen2.5-coder:14b

# 汎用（日本語対応）
ollama pull qwen2.5:7b
```

### 4. Claude Codeでの使用（オプション）

```bash
# 環境変数を設定してローカルLLMに向ける
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama  # 形式上必要なダミー値

# Claude Codeを起動
claude --model qwen2.5-coder:7b
```

### 5. Python経由での使用

```bash
pip install openai  # OllamaはOpenAI互換APIも提供
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # ダミー値
)

response = client.chat.completions.create(
    model="qwen2.5-coder:7b",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
```

## モデル比較

| モデル | サイズ | 特徴 | 推奨用途 |
|--------|--------|------|---------|
| qwen2.5-coder:7b | 4.7GB | コード特化・速い | 日常的なコード生成 |
| qwen2.5-coder:14b | 9GB | 高精度・やや遅い | 複雑なコードタスク |
| qwen2.5:7b | 4.7GB | 汎用・日本語対応 | 対話・文章生成 |
| llama3.1:8b | 4.9GB | 汎用 | 一般タスク |

## 動作確認

```bash
# Ollamaが起動しているか確認
curl http://localhost:11434/api/tags

# モデル一覧を確認
ollama list

# 簡単なテスト
ollama run qwen2.5-coder:7b "Pythonでフィボナッチ数列を出力する関数を書いて"
```

## トラブルシュート

### ツール非対応エラーが出る
→ `qwen2.5-coder` 系モデルに変更する。ツール呼び出しに対応している。

### 生成が遅い・不安定
→ メモリ不足の可能性。`Activity Monitor`でメモリ圧迫を確認。7Bモデルでも16GB推奨。

### `ollama serve` が既に起動中というエラー
```bash
# プロセスを確認して停止
pkill ollama
ollama serve
```

### Claude Codeがローカルに接続できない
→ `ANTHROPIC_BASE_URL` に `/v1` を付けた形式を試す:
```bash
export ANTHROPIC_BASE_URL=http://localhost:11434/v1
```

## スキル（Skills）機能

ローカルLLMの回答品質をタスク特化の「教科書」で引き上げる仕組み。

```bash
# スキルを指定して起動
python scripts/agent.py --skill tech_writing_ja

# 利用可能なスキル一覧
python scripts/agent.py --list-skills

# スキルあり・なしの比較実験
python examples/compare_skills.py qwen2.5:7b tech_writing_ja "量子コンピュータを説明して"
```

| スキルファイル | 用途 |
|---|---|
| `skills/tech_writing_ja.md` | 技術文書の分かりやすい解説 |
| `skills/code_review.md` | コードレビュー |
| `skills/template.md` | 新規スキル作成テンプレート |

詳しくは `skills/README.md` を参照。

## 参考リンク

- [Ollama公式ドキュメント](https://docs.ollama.com/)
- [Ollama × Claude Code 統合ガイド](https://docs.ollama.com/integrations/claude-code)
- [Zenn: ローカルLLMでClaude Codeを動かす](https://zenn.dev/urakawa_jinsei/articles/2b707394d6c216)
