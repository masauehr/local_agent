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

または `start.sh`（**推奨・後述のコンテキスト削減設定込み**）:

```bash
./start.sh qwen3.6:35b-mlx
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

---

## 巨大コンテキストによるタイムアウト問題と対策（2026-08-12追記）

### 症状

`ollama pull <model>` で以下のエラーが出ることがある。

```
Error: pull model manifest: 412:
The model you are attempting to pull requires a newer version of Ollama.
```

→ **原因はダウンロード失敗ではなくOllama本体が古いこと。** `brew upgrade ollama` で更新すれば解決する（Homebrewでインストールしている場合。`ollama --version` で確認）。

また、`start.sh` や `ollama launch claude` でローカルモデルを起動し、Claude Code内でメッセージを送っても長時間応答が返らず、最終的に **API error** になることがある。

### 原因調査でわかったこと

`/opt/homebrew/var/log/ollama.log` を見ると、内部の `/v1/completions` 自体は成功している（`status="200 OK"`）にもかかわらず、それをラップする `/v1/messages?beta=true` が**約5分（4分50秒〜5分前後）で毎回500エラー**になっていた。これはモデルやバックエンド（MLX / llama.cpp GGUF）を問わず共通して発生した。

原因は**コンテキストサイズと処理時間**だった。Claude Codeの初回リクエストは、`CLAUDE.md`だけでなく以下も毎回システムプロンプトとして送信するため、思った以上に巨大になる。

| 要素 | 目安の重さ |
|------|-----------|
| ユーザー/プロジェクト/リポジトリの`CLAUDE.md`合計 | 数千トークン程度（軽い。**犯人ではない**） |
| ツール定義本体（特に`Agent`・`Artifact`は説明文が長大） | 重い |
| 接続中のMCPサーバーのツール一覧（Gmail/Calendar/Drive等） | 非常に重い（数万トークン級） |
| スキル一覧の説明文 | 中程度 |
| 追加ワーキングディレクトリ・git status等の環境情報 | 軽い |

実測では、フル構成で**約107,000トークン**、MCPを除外しても**約68,000トークン**になっていた。ローカルモデルはこの規模のプロンプト処理に数分かかり、Claude Code側（または`/v1/messages`変換層）のタイムアウト（体感約5分）に間に合わず失敗していた。

**なお「コンテキストウィンドウの上限」自体は問題ではない。** 主要モデルはいずれも10万トークン超を余裕で収容できる。

| モデル | パラメータ数 | コンテキスト上限 |
|---|---|---|
| muse-glimmer:30b-mlx | 32.3B | 131,072 |
| qwen3.6:35b-mlx | 35.1B | 262,144 |
| qwen3.6:27b-mlx | 27.4B | 262,144 |
| devstral-small-2:24b | 24.0B | 393,216 |

問題は「入るか」ではなく「時間内に処理し終わるか」。軽量モデル（パラメータ数が少ない）ほど処理速度は速くなるため、タイムアウト回避には有利。

### 対策（`start.sh`に実装済み）

CLAUDE.mdは軽量で作業の継続性（コーディング規約・ドキュメント更新ルール等の一貫性）に有用なため残しつつ、重い部分だけを削減する。

```bash
claude --model "$MODEL" --strict-mcp-config --tools Bash,Edit,Write,Read,WebSearch,WebFetch,TodoWrite
```

- `--strict-mcp-config`：MCPサーバーのツール一覧を読み込まない（指定なし＝MCP完全除外）。最も効果が大きい
- `--tools`：`Agent`・`Artifact`など説明文が長大なツールを除外し、基本ループ（読み書き・実行）＋調べ物（WebSearch/WebFetch）＋進捗管理（TodoWrite）だけに絞る
- `CLAUDE.md`は明示的に除外しない（`--bare`は使わない）→ 規約・ルールの継続性を保つ

この設定で、107,000トークン規模だった初回リクエストが数千〜1万トークン程度まで下がり、応答時間は**5分タイムアウト→20〜30秒**まで改善した。

> より強く削りたい場合は `--bare`（CLAUDE.md自動読込・auto-memory・フック等も全部スキップする最小モード）や `--safe-mode`（CLAUDE.md/スキル/プラグイン/MCP等を全無効化）もある。ただし規約の継続性は失われる。

### プレフィックスキャッシュの挙動

一度モデルがロードされ会話が続いている間は、Ollama側のプレフィックスキャッシュにより**新規発話分のトークンだけ**処理すれば済むため、2回目以降の応答はほぼ一瞬になる（例: 26,251トークン中、新規処理はわずか27トークン）。

ただし以下の場合はキャッシュが失われ、次回また初回同様の待ち時間になる。
- モデルがアイドルタイムアウトでアンロードされた場合（`ollama ps`のUNTIL欄が目安）
- 会話を`/clear`した・巻き戻した場合

### ローカルモデルのgit push挙動について

ローカルモデルに「ファイルを作ってpushして」と依頼したところ、`main`に直接pushせず**新規ブランチを作成してそこにpush**するという安全側の挙動を確認した（GitHubの「Compare & pull request」表示はこの新規ブランチpushに対する通常の案内であり、エラーではない）。ただし`main`へのマージ判断はしないため、テスト用ブランチは手動で確認・削除（`git branch -D`, `git push origin --delete`）する必要がある。

#### Git運用ルールとブランチ運用

本プロジェクトでは以下のGit運用ルールを守ること。

- **既定ブランチ（main）への直接コミットは禁止**。作業は必ず機能ブランチで実施し、mainへはマージして反映する。
- ファイルの追加・変更時は `git add → git commit → git push` の3ステップを必ず実行する。コミットメッセージ末尾には `Co-Authored-By: Claude <noreply@anthropic.com>` を付ける。
- push前には必ずユーザーに確認を取る（破壊的操作防止）。
- 2026-08-12時点の運用では、Claude Codeの安全ルールによりmainブランチ上での作業時は自動的に作業ブランチが作成される。運用簡略化が必要な場合はマニュアル記載どおりブランチを手動で管理する。

この運用は `pc_docs/manuals/automation/local-llm-agent.md` と `~/projects/local_agent/CLAUDE.md` に記載のGitHub更新ルールに基づく。

---

## モデル別の応答速度比較（2026-08-13追記）

同一マシン（64GB統合メモリ搭載Mac）上での実測で、応答速度は以下の順になった。

**qwen3.6:35b-mlx（最速） ＞ muse-glimmer:30b（GGUF/llama.cpp版） ＞ muse-glimmer:30b-mlx（最遅）**

`ollama show` で内部構造を比較すると、構造的な理由がはっきり見える。

| モデル | アーキテクチャ | 総パラメータ | 埋め込み次元 | 量子化 |
|---|---|---|---|---|
| qwen3.6:35b-mlx | **qwen3_5_moe**（MoE） | 35.1B（実活性化は約3B） | **2048** | nvfp4 |
| muse-glimmer:30b-mlx | muse_glimmer（**Dense**） | 32.3B（全パラメータ活性化） | **6656** | nvfp4 |
| muse-glimmer:30b（GGUF） | muse-glimmer（**Dense**） | 27.9B（全パラメータ活性化） | **6656** | Q4_K_M |

### ① qwen3.6が圧倒的に速い理由：MoE構造 × 小さい埋め込み次元

- qwen3.6は**MoE**（Mixture of Experts）で、35Bのうち**実際に計算するのは約3B分だけ**。muse-glimmer系は**Dense**（全パラメータが毎トークン計算に参加）なので、名目上のパラメータ数（30B級 vs 35B）以上に、**実計算量は10倍近い差**がある。
- さらに埋め込み次元（隠れ層の幅）がqwen3.6は2048、muse-glimmerは6656と**3倍以上**。Attention/FFN層の計算量はこの次元にほぼ比例〜二乗で効くため、これも大きく効いている。
- 量子化(nvfp4)は両者共通のため、ここは差の要因ではない。

### ② muse-glimmerの中でGGUF＞MLXだった理由

同じDense構造・同程度パラメータ数のため①ほどの構造差はない。以下2点が要因と考えられる。

- **量子化形式の違い**：GGUFは`Q4_K_M`（llama.cppで長年チューニングされてきた伝統的な量子化＋Metalカーネル）、MLX版は`nvfp4`（NVIDIA発の比較的新しい4bit形式）。nvfp4のMLX上でのカーネル実装がまだ成熟しておらず、逆量子化のオーバーヘッドが大きい可能性がある。
- **エンジンの成熟度**：llama.cppのMetalバックエンドはApple Silicon向けプロンプト処理の最適化が長年蓄積されているのに対し、Ollamaの`mlx-engine`は比較的新しい統合で、プリフィル（プロンプト処理）のチューニングがまだ追いついていない可能性がある。

### 結論・実用上の指針

- **MoE構造のモデル（qwen3.6系）を優先的に使う**のが速度面で最も効果が大きい。Dense構造のモデル（muse-glimmer系）は名目パラメータ数が近くても実計算量が大きく、体感速度が大きく劣る。
- 同じDenseモデルを使うなら、**GGUF（llama.cpp）版の方がMLX版より速い場合がある**。「MLX = Apple最適化だから常に速い」とは限らない点に注意。
