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

---

## スキル（Skills）実験 — 追加経緯と現状

### 背景
shi3zblog の記事（ https://note.com/shi3zblog/n/nd5954b2b6b94 ）で言及された「スキル」概念を実装・検証するために追加。  
スキル = **AI向け教科書（Markdownファイル）**。システムプロンプトとして渡すことで、低性能なローカルLLMでも特定タスクの精度を引き上げられるか試す実験。

### このプロジェクトの位置づけ整理
- **本来の local_agent の目的**: Claude Code CLI の裏側を Ollama に差し替えて動かす
- **スキル実験（今回追加）**: 自作 Python CLI で Ollama を直接叩き、スキルありなしの効果を比較する
- → 両者は独立。スキル実験は `scripts/agent.py` と `examples/compare_skills.py` で完結する

### 追加されたファイル構成
```
local_agent/
├── scripts/
│   ├── agent.py          # --skill フラグ追加済み（スキルをシステムプロンプトに読み込む）
│   └── skill_loader.py   # スキルファイル読み込みユーティリティ
├── skills/
│   ├── README.md         # スキルの書き方ガイド
│   ├── template.md       # 新規スキル作成テンプレート
│   ├── tech_writing_ja.md # 技術文書作成スキル（実用例）
│   └── code_review.md    # コードレビュースキル
└── examples/
    └── compare_skills.py  # スキルあり・なしの回答を並べて比較する実験スクリプト
```

### 次にやること（続きから始める手順）
1. Ollama の起動確認とモデル確認
   ```bash
   ollama list
   ```
2. 比較実験を実行してスキルの効果を確認
   ```bash
   source .venv/bin/activate
   python3 examples/compare_skills.py <モデル名> tech_writing_ja "DNSとは何ですか"
   ```
3. 結果を見て、スキルファイルの内容を改善する（`skills/` 配下を編集）
4. 新しいタスク向けのスキルを `skills/template.md` を元に作成する

### スキルファイルの仮想環境
Python の依存パッケージは `.venv/` に入っている。  
```bash
source .venv/bin/activate
```
