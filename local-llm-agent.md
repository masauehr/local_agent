# ローカルLLMエージェント（local_agent）セットアップ・操作マニュアル

## 概要

ローカルLLM（Ollama / llama.cpp / mlx_lm）に**スキル**（タスク特化のMarkdownファイル）を与えて、回答品質・フォーマット・言語制御を向上させる仕組みを実験・改善するプロジェクト。ファイル操作・git操作を自然言語で実行できるエージェント機能も実装済み。

- **プロジェクトディレクトリ**: `~/projects/local_agent/`
- **LLMサーバー**: Ollama（`http://localhost:11434`）または llama-server（`http://localhost:8080`）
- **推奨モデル**: `qwen3.6:35b-mlx`（Ollama・MLX最適化・MoE構造）
- **Python仮想環境**: `.venv/`

> 詳細: [README.md](../../local_agent/README.md), [CLAUDE.md](../../local_agent/CLAUDE.md), [LLM.md](../../local_agent/LLM.md)  
> MacBook Air 8GBの実験記録: [SLM.md](../../local_agent/SLM.md)

---

## プロジェクトの目的

**スキル**（タスク特化のMarkdownファイル）をシステムプロンプトとして渡すことで、ローカルLLMの回答品質・フォーマット・言語制御を向上させる仕組みを実験・改善する。

あわせて、ファイル操作・git操作を自然言語で実行できるエージェント機能も実装済み。

---

## ディレクトリ構成

```
local_agent/
├── scripts/
│    ├── agent.py              # インタラクティブエージェント（ツール呼び出し対応）
│    └── skill_loader.py       # スキルファイル読み込みユーティリティ
├── skills/                    # スキルファイル（LLMへの専門指示書）
│    ├── tech_writing_ja.md    # 技術文書作成スキル
│    ├── code_review.md        # コードレビュースキル
│    ├── debug_helper.md       # デバッグ支援スキル
│    ├── commit_message.md     # コミットメッセージ生成スキル
│    ├── regex_explainer.md    # 正規表現解説・生成スキル
│    ├── git_commit_push.md    # git全自動実行（status→add→commit→push）
│    ├── git_status.md         # git status専用（1ステップ）
│    ├── git_add.md            # git add . 専用（1ステップ）
│    ├── git_commit.md         # git commit 専用（1ステップ）
│    ├── git_push.md           # git push 専用（1ステップ）
│    ├── template.md           # 新規スキル作成テンプレート
│     └── README.md            # スキルの書き方ガイド
├── examples/
│    ├── basic_chat.py         # 基本チャットサンプル
│    ├── compare_skills.py     # スキルあり・なしの回答を比較
│     └── tool_use_test.py     # ツール呼び出し動作確認
├── setup/
│     └── install.sh           # 初回セットアップ
├── start.sh                   # Claude Code をローカルLLMで起動
├── CLAUDE.md                  # プロジェクト設定・技術スタック
├── LLM.md                     # ローカルLLM調査まとめ（64GB Mac向け）
├── SLM.md                     # SLM実験記録（8GB Mac向け）
└── README.md                  # プロジェクト概要
```

---

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

---

## MLXモデルについて（2026-05-22更新）

Ollamaには2種類のモデル種別がある。`-mlx`と`-cloud`で動作が全く異なるので注意。

| タグ | 実行場所 | 課金 |
|------|---------|------|
| `-mlx`（例: `qwen3.6:35b-mlx`） | **ローカル**（MLX / Apple Silicon最適化） | なし |
| `-cloud`（例: `gemma4:31b-cloud`） | **クラウド API 経由** | **課金あり** |

SIZEが`-`のモデルはローカルにファイルが存在せず、クラウドAPI経由で実行される。`ollama launch claude` で`-cloud`モデルを指定すると課金対象となるので注意。

---

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

### スキルの使い方

```bash
# スキルを指定してエージェント起動
python3 scripts/agent.py --skill tech_writing_ja

# 利用可能なスキル一覧を確認
python3 scripts/agent.py --list-skills
```

### スキルあり・なしの比較実験

```bash
source .venv/bin/activate
python3 examples/compare_skills.py <モデル名> <スキル名> "<質問>"

# 例
python3 examples/compare_skills.py qwen3.6:35b-mlx tech_writing_ja "DNSとは何ですか"
```

### 新しいスキルの作り方

```bash
cp skills/template.md skills/<新しいスキル名>.md
# テンプレートを編集してタスク固有の指示を記述
```

---

## ツール呼び出し機能（agent.py）

`agent.py` はLLMからのツール呼び出しに対応しており、ファイル操作・git操作を自然言語で実行できる。

### 利用可能なツール

| ツール名 | できること | 安全制限 |
|---------|-----------|---------|
| `calculate` | 数式計算 | mathモジュールのみ使用可 |
| `read_file` | テキストファイルの読み込み | カレントディレクトリ内のみ |
| `write_file` | ファイルの作成・上書き | カレントディレクトリ内のみ |
| `list_files` | ディレクトリ一覧の取得 | カレントディレクトリ内のみ |
| `run_git` | git操作 | `status/add/commit/push/diff/log/show` のみ許可 |

### 使用例

エージェントに自然言語で話しかけるだけで、対応するツールが自動呼び出される：

```
[あなた] このディレクトリのファイル一覧を見せて
   [ツール] list_files({})

[あなた] testと書かれたtest2.txtを作成して
   [ツール] write_file({"path": "test2.txt", "content": "test"})

[あなた] git statusを確認して
   [ツール] run_git({"args": ["status"]})

[あなた] 変更を全てコミットして
   [ツール] run_git({"args": ["add", "."]})
   ※ コミットメッセージを聞かれるので入力する

[あなた] feat: 機能追加 でコミットして
   [ツール] run_git({"args": ["commit", "-m", "feat: 機能追加"]})

[あなた] pushして
   [ツール] run_git({"args": ["push"]})
```

### ツール呼び出しの仕組み

Ollamaモデルによってツール呼び出しの出力形式が異なる：

| 形式 | 対応モデル例 | agent.pyの処理 |
|------|------------|---------------|
| OpenAI API標準（`tool_calls`） | `qwen3.6:35b-mlx` / `gemma4:e2b` | そのまま処理 |
| `<tool_call>` タグ形式（テキスト） | `qwen2.5:7b` 等 | フォールバックパーサーで処理 |

### デバッグモード

ツール呼び出しがうまくいかない場合は `AGENT_DEBUG=1` で生の出力を確認できる：

```bash
AGENT_DEBUG=1 python3 scripts/agent.py
# [DEBUG] tool_calls=... content=... が表示される
```

---

## モデル一覧（64GB Mac 向け）

| モデル | バックエンド | ツール呼び出し | 日本語品質 |
|--------|------------|--------------|-----------|
| `qwen3.6:35b-mlx`（35B MoE / 3B活性） | Ollama MLX | ◎ 安定・**最新推奨** | ◎ |
| `gemma4:e2b`（31B Gemma系） | Ollama | ◎ 安定 | ◎ |
| `llm-jp4-thinking`（32B MoE / 3B活性） | Ollama GGUF | 未検証 | ◎ 日本語特化 |

## モデル一覧（8GB Mac 向け）

> 詳細な実験記録と環境別の推奨構成は [SLM.md](../../local_agent/SLM.md) を参照。

| モデル | バックエンド | ツール呼び出し | 日本語品質 |
|--------|------------|--------------|-----------|
| `gemma4:e2b`（5.1GB） | Ollama | ◎ 安定 | ◎ |
| `Bonsai-8B`（1.1GB） | llama-server | ○ 単発OK・連鎖は不安定 | ○ |
| `qwen2.5:7b`（4.7GB） | Ollama | △ 不安定 | △ 中国語漏れあり |

---

## ドキュメント一覧

| ファイル | 内容 |
|---------|------|
| [CLAUDE.md](../../local_agent/CLAUDE.md) | プロジェクト設定・技術スタック・MLXモデル解説 |
| [LLM.md](../../local_agent/LLM.md) | ローカルLLM調査まとめ（Mac / Apple Silicon / 64GB向け） |
| [SLM.md](../../local_agent/SLM.md) | 小サイズモデル実験記録（MacBook Air 8GB / Bonsai-8B等） |
| [README.md](../../local_agent/README.md) | プロジェクト概要・クイックスタート・スキル一覧 |

---

## 初回セットアップ

```bash
cd ~/projects/local_agent

# Ollama・モデル・Python仮想環境を一括セットアップ
bash setup/install.sh
```

セットアップ内容：
1. Ollama のインストール確認（未インストールなら Homebrew でインストール）
2. Ollama サーバーの起動確認
3. デフォルトモデルのダウンロード
4. Python 仮想環境（`.venv/`）の作成と `openai` パッケージのインストール

---

## Claude Code をローカルLLMで起動

### エイリアス（推奨）

```bash
# ollama launch claude でMLXモデルを指定（最新推奨）
ollama launch claude --model qwen3.6:35b-mlx
```

### 手動設定

```bash
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama
claude --model qwen3.6:35b-mlx
```

> **注意**: 起動時に「Do you want to use this API key?」と聞かれたら **「2. No (recommended)」** を選ぶ。

### Python エージェントを直接起動

```bash
cd ~/projects/local_agent
source .venv/bin/activate
python3 scripts/agent.py

# モデルを変更する場合
OLLAMA_MODEL=qwen3.6:35b-mlx python3 scripts/agent.py
```

---

## 動作確認

```bash
# Ollamaサーバーの確認
curl http://localhost:11434/api/tags

# ダウンロード済みモデルの確認
ollama list

# Pythonスクリプトで確認
source .venv/bin/activate
python3 examples/basic_chat.py
```

---

## MLX / llama.cpp サーバー連携

### mlx_lm（mlx-lm）でAPIサーバー起動

```bash
pip install mlx-lm
mlx_lm.server --model mlx-community/Qwen2.5-32B-Instruct-4bit
# localhost:8080 でOpenAI互換APIとして動作
```

### Continue.dev への設定（例: Bonsai 8B）

`~/.continue/config.yaml` に以下を追加:

```yaml
models:
   - name: Bonsai 8B（1ビット量子化・ローカル）
     provider: openai
     model: bonsai-8b
     apiBase: http://localhost:8080/v1
     apiKey: dummy
     contextLength: 8192

mcpServers:
   - name: jma
     command: python3
     args:
        - /Users/masahiro/projects/jma_mcp/server.py
```

### メモリ不足で起動失敗する場合（8GB MacBook）

`common.sh` の `CTX_SIZE_DEFAULT` を変更:

```sh
# ~/projects/1bit_LLM/bonsai-demo/scripts/common.sh
CTX_SIZE_DEFAULT=8192    # 0（自動）から変更
```

---

## MLXモデルの扱いに注意（2026-05-22追記）

### `-mlx` と `-cloud` の違い

| タグ | 実行場所 | 課金 |
|------|---------|------|
| `-mlx`（例: `qwen3.6:35b-mlx`） | **ローカル**（MLX / Apple Silicon最適化） | なし |
| `-cloud`（例: `gemma4:31b-cloud`） | **クラウド API 経由** | **課金あり** |

SIZEが`-`のモデルはOllamaがクラウドへ中継する。`ollama launch claude` で`-cloud`モデルを指定すると課金対象となるので注意。

### MoE（Mixture of Experts）モデルの活用

`qwen3.6:35b-mlx` はMoE構造で、35B総パラメータのうち推論時は3Bのみ活性化。
- 速い・メモリ効率が良い・高性能の三拍子
- Vision / Tools / Thinking 対応
- 262K トークンのネイティブコンテキスト

---

## HuggingFaceからのモデルDL（2026-05-24追記）

### `hf` コマンドのインストール

```bash
brew install hf
# または pip install huggingface-hub（注意: pip版は非推奨 → `huggingface-cli` は廃止済み）
```

### リポジトリのファイル一覧確認

```bash
hf models ls <user>/<repo>
# 例
hf models ls ash2813/llm-jp-4-32b-a3b-thinking-gguf
```

### モデルのDL方法

**方法1: Ollama で直接 pull（推奨）**

```bash
# デフォルト量子化
ollama pull hf.co/<user>/<repo>

# 量子化を指定
ollama pull hf.co/<user>/<repo>:<filename>.gguf
```

**方法2: hf download → Modelfile 登録**

```bash
hf download <user>/<repo> <filename>.gguf --local-dir ~/models/
echo "FROM $HOME/models/<filename>.gguf" > /tmp/Modelfile
ollama create <model-name> -f /tmp/Modelfile
```

---

## LLM-jp-4（国産LLM）のテスト（2026-05-24追記）

国立情報学研究所（NII）が公開した国産LLM。日本語MT-BenchでGPT-4oを上回る性能。

- **リポジトリ**: `ash2813/llm-jp-4-32b-a3b-thinking-gguf`
- **推奨ファイル**: `llm-jp-4-32b-a3b-thinking-Q4_K_M.gguf`（約20GB）
- **アーキテクチャ**: 32B MoE（A3B活性パラメータ）・thinking対応

### Ollamaへの登録手順

```bash
# 1. pull（約20GBのDL）
ollama pull hf.co/ash2813/llm-jp-4-32b-a3b-thinking-gguf:llm-jp-4-32b-a3b-thinking-Q4_K_M.gguf

# 2. local_agent.py で動作テスト
/opt/anaconda3/bin/python3 ~/projects/ai_news/scripts/local_agent.py \
  --model hf.co/ash2813/llm-jp-4-32b-a3b-thinking-gguf:llm-jp-4-32b-a3b-thinking-Q4_K_M.gguf \
  --mode weekly --week-file XXXX --week-label "..." --year 2026 --month XX
```

### Claude Code では使えない点に注意

Claude CodeはAnthropicのAPIに固定されており、ローカルGGUFモデルを直接指定できない。
LiteLLMプロキシ経由で接続する方法はあるが、tool calling等の互換性が不完全で実用的ではない。
**ローカルモデルのテストは `local_agent.py` を使って行うこと。**

---

## ローカルLLMでのMCP利用の注意点

| 項目 | 内容 |
|------|------|
| **同時実行禁止** | llama-server は並列リクエスト非対応。Continue と他CLIを同時に使わない |
| **コンテキスト制限** | 8192トークンのため、長い会話後はツール結果が上限を超えやすい |
| **エリアコードの型** | LLMが整数で渡す場合あり。jma-mcp の server.py は `str()` 変換・`anyOf` スキーマで対応済み |
| **ツール選択の精度** | 「沖縄の最高気温」のような地域絞り込みは `get_mdrr_data` を使うよう誘導が必要 |
| **長い出力は苦手** | Bonsai 8B は100行超の生成でハルシネーションが増える |
