# local_agent

ローカルLLM（Ollama / llama.cpp）にスキルを与えて、タスク特化型AIエージェントを構築・実験するプロジェクト。

> 詳しい仕組み・実験結果・トラブルシューティングは [local-llm-agent.md](local-llm-agent.md) を参照。

## プロジェクトの目的

**スキル**（タスク特化のMarkdownファイル）をシステムプロンプトとして渡すことで、ローカルLLMの回答品質・フォーマット・言語制御を向上させる仕組みを実験・改善する。

あわせて、ファイル操作・git操作を自然言語で実行できるエージェント機能も実装済み。

## ディレクトリ構成

```
local_agent/
├── scripts/
│   ├── agent.py            # インタラクティブエージェント（ツール呼び出し対応）
│   └── skill_loader.py     # スキルファイル読み込みユーティリティ
├── skills/                 # スキルファイル（LLMへの専門指示書）
│   ├── tech_writing_ja.md  # 技術文書作成スキル
│   ├── code_review.md      # コードレビュースキル
│   ├── debug_helper.md     # デバッグ支援スキル
│   ├── commit_message.md   # コミットメッセージ生成スキル
│   ├── regex_explainer.md  # 正規表現解説・生成スキル
│   ├── template.md         # 新規スキル作成テンプレート
│   └── README.md           # スキルの書き方ガイド
├── examples/
│   ├── basic_chat.py       # 基本チャットサンプル
│   └── compare_skills.py   # スキルあり・なしの回答を比較する実験スクリプト
├── setup/
│   └── install.sh          # 初回セットアップ
└── CLAUDE.md               # このプロジェクトへの指示
```

## クイックスタート

### エイリアスで起動（推奨）

```bash
bllama    # Bonsai-8B 用 llama-server を起動（先に実行しておく）
lagent    # llama-server + Bonsai-8B で agent.py を起動（bllama が前提）
```

> エイリアスは `~/.bash_profile` に登録済み（当初 `.zshrc` に設定していたが移行）。

> **注意**: `lagent` だけで起動してもスキルは読み込まれない。スキルは起動時に `--skill` で指定する必要がある。チャット中に「スキルを読んで」と言っても、会話の文脈に読み込まれるだけでシステムプロンプトには反映されない。

```bash
lagent --skill git_commit_push   # スキルを指定して起動
```

### 直接起動する場合

```bash
cd ~/projects/local_agent
source .venv/bin/activate

# デフォルト（Bonsai-8B + スキルなし）※llama-server が起動済みであること
python3 scripts/agent.py

# スキルを指定して起動
python3 scripts/agent.py --skill tech_writing_ja

# 利用可能なスキル一覧を確認
python3 scripts/agent.py --list-skills
```

## スキル機能

スキルとは**LLMへの専門指示書**。システムプロンプトとして渡すことで以下が向上する：
- 回答のフォーマット・構造化
- 言語制御（中国語漏れの防止等）
- 過剰な回答の抑制

### スキル一覧

| スキル名 | 用途 |
|---------|------|
| `tech_writing_ja` | 技術文書を「一言・詳細・具体例・注意点」の構造で出力 |
| `code_review` | 「重大な問題→改善提案→良い点→修正コード」の形式でレビュー |
| `debug_helper` | エラーから「種類→原因→修正方法→確認手順」を提示 |
| `commit_message` | diffから `feat/fix/refactor` 等のprefixつきメッセージを生成 |
| `regex_explainer` | 正規表現を解説・生成・デバッグ。パーツ表・マッチ例つき |
| `git_commit_push` | status→add→commit→push を全自動実行。メッセージも自動生成 |
| `git_status` | git status を呼んで結果を表示（1ステップ専用） |
| `git_add` | git add . → status 確認（1ステップ専用） |
| `git_commit` | status 確認 → commit（メッセージ自動生成）（1ステップ専用） |
| `git_push` | push → log 確認（1ステップ専用） |

### スキルあり・なしの比較実験

```bash
python3 examples/compare_skills.py <モデル名> <スキル名> "<質問>"

# 例
python3 examples/compare_skills.py gemma4:e2b tech_writing_ja "DNSとは何ですか"
python3 examples/compare_skills.py gemma4:e2b code_review "以下をレビューして: def f(x): return eval(x)"
```

### 新しいスキルの作り方

```bash
cp skills/template.md skills/<新しいスキル名>.md
# テンプレートを編集してタスク固有の指示を記述
```

## ツール呼び出し機能

エージェントに自然言語で話しかけると、対応するツールが自動で呼び出される。

| ツール | できること |
|--------|-----------|
| `list_files` | ディレクトリ一覧の取得 |
| `read_file` | テキストファイルの読み込み |
| `write_file` | ファイルの作成・上書き |
| `calculate` | 数式計算 |
| `run_git` | git操作（status/add/commit/push/diff/log/show） |

```
[あなた] このディレクトリのファイル一覧を見せて
[あなた] test3.txtを作成してtestと書いて
[あなた] git add . してfeat: テスト でコミットして
[あなた] pushして
```

## 対応モデル・バックエンド

| モデル | バックエンド | ツール呼び出し | 日本語品質 |
|--------|------------|--------------|-----------|
| `gemma4:e2b`（5.1GB） | Ollama | ◎ 安定・**推奨** | ◎ |
| `qwen2.5:7b`（4.7GB） | Ollama | △ 不安定 | △ 中国語漏れあり |
| `Bonsai-8B`（1.1GB） | llama-server | ○ 単発OK・連鎖は不安定 | ○ |

### Ollamaで起動する場合

```bash
# Ollamaサーバーが起動していること
ollama list

# モデルを指定して起動
OLLAMA_MODEL=gemma4:e2b python3 scripts/agent.py
```

### Bonsai（llama-server）で起動する場合

```bash
# llama-serverを起動
cd ~/projects/1bit_LLM/bonsai-demo
./scripts/start_llama_server.sh &

# agent.pyをBonsaiに向ける
cd ~/projects/local_agent
OLLAMA_BASE_URL=http://localhost:8080/v1 OLLAMA_MODEL=bonsai-8b python3 scripts/agent.py
```

## デバッグ

```bash
# ツール呼び出しの生出力を確認
AGENT_DEBUG=1 python3 scripts/agent.py
```
