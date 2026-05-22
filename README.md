# local_agent

ローカルLLM（Ollama / llama.cpp / mlx_lm）にスキルを与えて、タスク特化型AIエージェントを構築・実験するプロジェクト。

> 詳しい仕組み・実験結果・トラブルシューティングは [local-llm-agent.md](local-llm-agent.md) を参照。

## プロジェクトの目的

**スキル**（タスク特化のMarkdownファイル）をシステムプロンプトとして渡すことで、ローカルLLMの回答品質・フォーマット・言語制御を向上させる仕組みを実験・改善する。

あわせて、ファイル操作・git操作を自然言語で実行できるエージェント機能も実装済み。

## ドキュメント

| ファイル | 内容 |
|---------|------|
| [CLAUDE.md](CLAUDE.md) | プロジェクト設定・技術スタック・MLXモデル解説 |
| [LLM.md](LLM.md) | ローカルLLM調査まとめ（Mac / Apple Silicon / 64GB向け） |
| [SLM.md](SLM.md) | 小サイズモデル実験記録（MacBook Air 8GB / Bonsai-8B等） |
| [local-llm-agent.md](local-llm-agent.md) | 詳細マニュアル・操作手順・トラブルシューティング |

## ディレクトリ構成

```
local_agent/
├── scripts/
│    ├── agent.py             # インタラクティブエージェント（ツール呼び出し対応）
│    └── skill_loader.py      # スキルファイル読み込みユーティリティ
├── skills/                   # スキルファイル（LLMへの専門指示書）
│    ├── tech_writing_ja.md   # 技術文書作成スキル
│    ├── code_review.md       # コードレビュースキル
│    ├── debug_helper.md      # デバッグ支援スキル
│    ├── commit_message.md    # コミットメッセージ生成スキル
│    ├── regex_explainer.md   # 正規表現解説・生成スキル
│    ├── git_commit_push.md   # git全自動実行（status→add→commit→push）
│    ├── git_status.md        # git status専用（1ステップ）
│    ├── git_add.md           # git add . 専用（1ステップ）
│    ├── git_commit.md        # git commit 専用（1ステップ）
│    ├── git_push.md          # git push 専用（1ステップ）
│    ├── template.md          # 新規スキル作成テンプレート
│    └── README.md            # スキルの書き方ガイド
├── examples/
│    ├── basic_chat.py        # 基本チャットサンプル
│    ├── compare_skills.py    # スキルあり・なしの回答を比較
│    └── tool_use_test.py     # ツール呼び出し動作確認
├── setup/
│    └── install.sh           # 初回セットアップ
├── start.sh                 # Claude Code をローカルLLMで起動
├── CLAUDE.md                # プロジェクト設定・技術スタック
├── LLM.md                   # ローカルLLM調査まとめ（64GB Mac向け）
├── SLM.md                   # SLM実験記録（8GB Mac向け）
└── local-llm-agent.md       # 詳細マニュアル
```

## クイックスタート

### Claude Code をローカルLLMで起動（推奨）

```bash
ollama launch claude --model qwen3.6:35b-mlx
```

または手動設定:

```bash
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama
claude --model qwen3.6:35b-mlx
```

### Python エージェント起動

```bash
cd ~/projects/local_agent
source .venv/bin/activate

# デフォルトモデルで起動
python3 scripts/agent.py

# スキルを指定して起動
python3 scripts/agent.py --skill tech_writing_ja

# エージェント一覧を確認
python3 scripts/agent.py --list-skills
```

## 対応モデル・バックエンド

### 64GB Mac 向け（推奨）

| モデル | バックエンド | ツール呼び出し | 日本語品質 |
|--------|------------|--------------|-----------|
| `qwen3.6:35b-mlx`（35B MoE / 3B活性） | Ollama MLX | ◎ 安定・**最新推奨** | ◎ |
| `gemma4:e2b`（31B Gemma系） | Ollama | ◎ 安定 | ◎ |
| `qwen3.5:397b-cloud` | Ollama Cloud | △ | ○ |

### 8GB Mac 向け（SLM実験）

| モデル | バックエンド | ツール呼び出し | 日本語品質 |
|--------|------------|--------------|-----------|
| `gemma4:e2b`（5.1GB） | Ollama | ◎ 安定 | ◎ |
| `Bonsai-8B`（1.1GB） | llama-server | ○ 単発OK・連鎖は不安定 | ○ |
| `qwen2.5:7b`（4.7GB） | Ollama | △ 不安定 | △ 中国語漏れあり |

> 詳細な実験記録と環境別の推奨構成は [SLM.md](SLM.md) を参照。

### MLXモデルについて

Ollamaには2種類のモデル種別がある。`-mlx`と`-cloud`で動作が全く異なるので注意。

| タグ | 実行場所 | 課金 |
|------|---------|------|
| `-mlx`（例: `qwen3.6:35b-mlx`） | **ローカル**（MLX / Apple Silicon最適化） | なし |
| `-cloud`（例: `gemma4:31b-cloud`） | **クラウド API 経由** | **課金あり** |

SIZEが`-`のモデルはローカルにファイルが存在せず、クラウドAPI経由で実行される。`ollama launch claude` で`-cloud`モデルを指定すると課金対象となるので注意。

## スキル機能

スキルとは**LLMへの専門指示書（Markdownファイル）**。システムプロンプトとして渡すことで、以下が向上する：
- 回答のフォーマット・構造化
- 言語制御（中国語漏れの防止等）
- 過剰な回答の抑制

### スキル一覧

| スキル名 | 用途 |
|---------|------|
| `tech_writing_ja` | 技術文書を「一言・詳細・具体例・注意点」の構造で出力 |
| `code_review` | 「重大な問題→改善提案→良い点→修正コード」の形式でレビュー |
| `debug_helper` | エラーから「種類→原因→修正方法→確認手順」を提示 |
| `commit_message` | diffから `feat/fix/refactor` 等のprefixつきコミットメッセージを生成 |
| `regex_explainer` | 正規表現を解説・生成・デバッグ。パーツ表・マッチ例つき |
| `git_commit_push` | status→add→commit→push を全自動実行 |
| `git_status` | git status を呼んで結果を表示（1ステップ専用） |
| `git_add` | git add . → status 確認（1ステップ専用） |
| `git_commit` | status 確認 → commit（メッセージ自動生成）（1ステップ専用） |
| `git_push` | push → log 確認（1ステップ専用） |

### スキルあり・なしの比較実験

```bash
python3 examples/compare_skills.py <モデル名> <スキル名> "<質問>"

# 例
python3 examples/compare_skills.py qwen3.6:35b-mlx tech_writing_ja "DNSとは何ですか"
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

## デバッグ

```bash
# ツール呼び出しの生出力を確認
AGENT_DEBUG=1 python3 scripts/agent.py
```
