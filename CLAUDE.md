# CLAUDE.md — local_agent プロジェクト

## プロジェクト概要

ローカルLLM（Ollama / llama.cpp / mlx_lm）に**スキル**（タスク特化のMarkdownファイル）を与えて、回答品質・フォーマット・言語制御を向上させる仕組みを実験・改善するプロジェクト。

あわせて、ファイル操作・git操作を自然言語で実行できるツール呼び出し機能も実装・実験している。

- 古い環境（MacBook Air 8GB）の実験記録: [SLM.md](SLM.md)
- モデル比較・設定ガイド: [LLM.md](LLM.md)

## 技術スタック

- **ローカルLLMサーバー**: Ollama v0.15以降（MLX対応） / llama-server（llama.cpp） / mlx_lm
- **推奨モデル**: `qwen3.6:35b-mlx`（Ollama・MoE構造・35B総計/3B活性で高速推理）
- **言語**: Python 3.10以上
- **APIクライアント**: `openai` パッケージ（OpenAI互換）
- **接続先**: Ollama `http://localhost:11434` / llama-server `http://localhost:8080`

## MLXモデルについて（2026-05-22更新）

Ollamaには2種類のモデル種別がある。`-mlx`と`-cloud`で動作が全く異なるので注意。

| タグ | 実行場所 | 課金 | 説明 |
|------|---------|------|------|
| `-mlx`（例: `qwen3.6:35b-mlx`） | **ローカル**（MLX / Apple Silicon最適化） | なし | ローカルで推論。無料・最速 |
| `-cloud`（例: `gemma4:31b-cloud`） | **クラウド API 経由** | **課金あり** | Ollamaがクラウドへ中継する |

SIZEが`-`のモデルはローカルにファイルが存在せず、クラウドAPI経由で実行される。`ollama launch claude` で`-cloud`モデルを指定すると課金対象となるので注意。

### 推奨コマンド

```bash
# Claude Code をOllama経由（MLXローカル実行・無料）で起動
ollama launch claude --model qwen3.6:35b-mlx

# または環境変数を直接設定
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama
claude --model qwen3.6:35b-mlx
```

### 動作確認方法

Claude Code内で`/status`コマンドを実行し、ベースURLが`http://localhost:11434`になっていればOllama経由のローカル実行。`api.anthropic.com`であれば本番APIに接続され課金対象となる。

## ディレクトリ構成方針

```
local_agent/
├── scripts/          # エージェント本体・実行スクリプト（Pythonスネークケース）
├── setup/            # セットアップ用シェルスクリプト
├── examples/         # 動作確認・サンプルコード
└── docs/             # 追加ドキュメント（必要に応じて）
```

## コーディング規約

- **言語**: Python（スネークケース、インデント4スペース）
- **コメント**: 日本語で記述
- **APIキー**: コード内にハードコードしない。環境変数または `.env` で管理
- **Ollamaエンドポイント**: デフォルト `http://localhost:11434`（環境変数 `OLLAMA_BASE_URL` で上書き可能に設計）

## 開発方針

1. **シンプル優先**: 重厚なフレームワーク（LangChain等）は使わず、まず素のAPIで実装
2. **段階的拡張**: 動作確認できたら機能を追加していく
3. **ローカル完結**: 外部APIへの依存を最小化（実験・検証目的を除く）
4. **モデル非依存**: 特定モデルに依存しないよう、モデル名は設定から変更できる設計

## ローカルLLM特有の注意事項

- **ツール呼び出し**: 全モデルが対応しているわけではない。`qwen2.5-coder` 系はツール対応
- **レスポンス速度**: M4 Mac 32GB + 14Bモデルでも数十秒かかる場合がある。タイムアウトは長めに設定
- **ハルシネーション**: ローカルモデルはClaudeより不安定。出力の検証コードを添える
- **JSON出力**: 複雑な構造化出力はエラーになりやすい。シンプルな形式を優先

## よく使うコマンド

```bash
# Ollamaサーバー起動
ollama serve

# モデル一覧確認
ollama list

# Claude Codeをローカル（MLX）に向ける（推奨）
ollama launch claude --model qwen3.6:35b-mlx

# 従来方法（環境変数を直接設定）
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama
claude --model qwen3.6:35b-mlx

# Ollama API動作確認
curl http://localhost:11434/api/tags
```

## 実装時の留意点

- Ollama APIは `http://localhost:11434/api/` と `http://localhost:11434/v1/`（OpenAI互換）の両方を持つ
- Claude Code向けには `ANTHROPIC_BASE_URL=http://localhost:11434` （`/v1` なし）を使う
- Python `openai` パッケージ向けには `base_url="http://localhost:11434/v1"` を使う
- モデルが起動していない場合は最初のリクエストで自動ロードされるが時間がかかる

---

## スキル（Skills）実験 — 概要

shi3zblog の記事で言及された「スキル」概念（AI向け専門指示書Markdownファイル）を実装・検証。
スキル = **LLMへの専門指示書**。システムプロンプトとして渡すことで、回答のフォーマット・構造化・言語制御を向上できる。

- 詳細な実験記録: [SLM.md](SLM.md)（MacBook Air 8GBでの旧実験）

## スキルの実装

スキルは `scripts/agent.py` でシステムプロンプトとして読み込まれる。`--skill` フラグで特定のスキルファイルを指定できる。

```bash
# スキルありで起動
python3 scripts/agent.py --skill tech_writing_ja

# スキル一覧
python3 scripts/agent.py --list-skills
```

## ツール呼び出し機能

エージェントに自然言語で話しかけると、対応するツールが自動で呼び出される。

- 追加済みのツール: `write_file` / `list_files` / `run_git`
- フォールバック: `<tool_call>` テキスト形式パーサー（モデル非依存）

## MLXモデルの活用（2026-05-22更新）

MoE（Mixture of Experts）構造の `qwen3.6:35b-mlx` が最新推奨モデル。
- 35B総パラメータのうち推論時は3Bのみ活性化 → 高速・軽量
- `-mlx` タグでローカルMLX実行（無料・Apple Silicon最適化）
- `ollama launch claude --model qwen3.6:35b-mlx` で起動

詳細は [LLM.md](LLM.md) を参照。
