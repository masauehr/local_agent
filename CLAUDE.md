# CLAUDE.md — local_agent プロジェクト

## プロジェクト概要

ローカルLLM（Ollama）を使ったAIエージェント環境の構築・実験プロジェクト。
OllamaのAnthropic互換APIを通じて、APIコストゼロでAIエージェントを動かす。

## 技術スタック

- **ローカルLLMサーバー**: Ollama v0.15以降
- **主要モデル**: qwen2.5-coder:7b（デフォルト）
- **言語**: Python 3.10以上
- **APIクライアント**: `openai` パッケージ（OpenAI互換）または `httpx`（直接呼び出し）
- **接続先**: `http://localhost:11434`

## ディレクトリ構成方針

```
local_agent/
├── scripts/        # エージェント本体・実行スクリプト（Pythonスネークケース）
├── setup/          # セットアップ用シェルスクリプト
├── examples/       # 動作確認・サンプルコード
└── docs/           # 追加ドキュメント（必要に応じて）
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

# Claude Codeをローカルに向ける
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama
claude --model qwen2.5-coder:7b

# Ollama API動作確認
curl http://localhost:11434/api/tags
```

## 実装時の留意点

- Ollama APIは `http://localhost:11434/api/` と `http://localhost:11434/v1/`（OpenAI互換）の両方を持つ
- Claude Code向けには `ANTHROPIC_BASE_URL=http://localhost:11434` （`/v1` なし）を使う
- Python `openai` パッケージ向けには `base_url="http://localhost:11434/v1"` を使う
- モデルが起動していない場合は最初のリクエストで自動ロードされるが時間がかかる
