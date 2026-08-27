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

---

## qwen3.8 / nemotron-3.5-lightning 導入検証（2026-08-16追記）

### 検証したモデル

| モデル | アーキテクチャ | 総パラメータ | アクティブパラメータ | コンテキスト長 | リリース |
|---|---|---|---|---|---|
| `qwen3.8:27b-mlx` | **Dense**（Gated DeltaNet 48層＋Full-Attention 16層） | 27.78B（全活性化） | 27.78B | 262,144 | 2026-08-14 |
| `nemotron-3.5-lightning:30b-mlx` | **Hybrid MoE**（Mamba-2層＋MoE層＋一部Attention層） | 30B | 3B | 256K〜1M（バックエンド依存） | 2026-08-11頃 |

比較の基準として、同日に約9時間使用した`qwen3.6:35b-mlx`/`qwen3.6:27b-mlx`（08:01〜16:55、エラー0件）の実績も参照した。

### qwen3.8:27b-mlx: Claude Code連携で重大な互換性問題

2回の独立したセッション（17:42起動・18:13再起動）のいずれでも、`/v1/messages`へのリクエストが以下のエラーで頻発した。

```
level=ERROR source=routes.go:2684 msg="chat prompt error" error="system message must be at the beginning"
```

- 試行1（17:42:20起動）: 最初の1件のみ成功、以降11連続で500エラー→セッション停止
- 試行2（18:13:01再起動）: 5連続失敗→1件成功→7連続失敗→1件成功（mlx→GGUFへの自動フォールバックと同時）→5連続失敗→停止
- 本日発生した`system message`エラー全28件は、すべてqwen3.8使用中の時間帯（17:42〜18:15）に集中。同日約9時間動かした`qwen3.6`や、その後使用した`nemotron-3.5-lightning`では同エラーは一度も発生していない

**原因の推測**: Claude Codeは会話途中で`<system-reminder>`（コンテキスト圧縮通知・日付更新通知など）をsystem roleとして挿入することがある。Ollama側の`qwen3.8`向けチャットテンプレート処理（`renderer=qwen3.8` / `parser=qwen3.5`。公開2日目のためqwen3.5パーサーを暫定流用している）がこの構造を正しく扱えず、「systemメッセージは配列の先頭にしかあってはならない」という制約違反として拒否している可能性が高い。qwen3.6も同じparserだが`renderer=qwen3.5`であり、この差が影響していると考えられる。

**結論**: 2026-08-16時点、`qwen3.8:27b-mlx`はOllama経由のClaude Code連携では**実用不可**。リリース直後でOllama側の対応が追いついていない可能性が高く、Ollama/qwen3.8側のアップデートを待って再検証する。

### nemotron-3.5-lightning:30b-mlx: 互換性は良好だが応答速度に課題

`system message`エラーは1件も発生せず、構造的な互換性問題は見られなかった。プリフィル速度はMoE構造（3B活性）通り高速だった。

| プロンプト長 | 処理時間 | 実測プリフィル速度 |
|---|---|---|
| 22,055トークン | 約26秒 | 約850 tok/s |
| 9,756トークン | 約9秒 | 約1,080 tok/s |

一方でリクエスト全体の応答時間にはばらつきが大きく、本マニュアル前掲の「巨大コンテキストによるタイムアウト問題」と同じ**約5分でのタイムアウト（`context canceled`）が8件発生**した。200 OKで完了したケースでも1分41秒〜3分17秒かかっており、プリフィルは速いがデコード（生成）フェーズがボトルネックになっている可能性がある。mlx版が実行中にメモリ超過でGGUF版へ自動フォールバックする挙動も確認された。

**結論**: 互換性面では最有力候補だが、現状の応答速度では実用的なテンポとは言い難い。`start.sh`の`--strict-mcp-config`+`--tools`絞り込み設定の併用や、`OLLAMA_CONTEXT_LENGTH`のチューニングを行った上での再検証が必要。

### 2026-08-16時点のまとめ

| モデル | 互換性 | 速度 | 総合評価 |
|---|---|---|---|
| `qwen3.6:35b-mlx` / `qwen3.6:27b-mlx` | ◎ エラー0件 | ◎ | 引き続き最有力 |
| `qwen3.8:27b-mlx` | ❌ `system message`エラー多発 | 評価不能 | 現時点で見送り、Ollama側更新待ち |
| `nemotron-3.5-lightning:30b-mlx` | ◎ エラー0件 | △ 5分タイムアウト頻発 | 互換性は良好・速度は要改善 |

---

## qwen3.8の`system message`エラー、原因確定と修正確認（2026-08-17追記）

### 原因: Ollama側の既知バグだった

Ollama公式のGitHubで、まさに同一の事象を報告したIssue/PRが見つかった。

- **[Issue #17754](https://github.com/ollama/ollama/issues/17754)**: 「`qwen3.8:27b`で`500 system message must be at the beginning`が発生する」
- **[PR #17757](https://github.com/ollama/ollama/pull/17757)**: Qwenレンダラーが非先頭のシステムメッセージ（会話途中に挿入されるsystemメッセージ）を処理できるよう修正。2026-08-14にマージ済み

PRの説明によれば「コーディングクライアントが最初のユーザーターンの後に、実行時システムメッセージ（Claude Codeの`<system-reminder>`等に相当）を挿入した場合、以前はそれを拒否していた」とあり、当マニュアルで確認した「2ターン目以降で必ず失敗する」という挙動と完全に一致する。

修正はバージョン`v0.32.14`（2026-08-15リリース）に含まれる。

| バージョン | 日付 | 内容 |
|---|---|---|
| v0.32.12 | 8/14 | qwen3.8 27B対応追加（**バグ入りでリリース**） |
| v0.32.13 | 8/14 | qwen3.8 developer instructions対応 |
| **v0.32.14** | **8/15** | **`renderers/qwen: tolerate non-leading system messages` — このバグの修正** |

### 注意: `brew upgrade`だけでは反映されない

`brew upgrade ollama`でバイナリを更新しても、**既に起動中の`ollama serve`プロセス（`brew services`管理）はメモリ上の旧バージョンのまま動き続ける**ため、修正が反映されない。`ollama --version`の表示が新しくなっていても、実際にリクエストを処理しているサーバーのバージョンとは限らない点に注意。

```bash
# CLIバイナリのバージョン（更新されていても実態を反映しない場合がある）
ollama --version

# 稼働中サーバーの実バージョンを確認（こちらが実態）
curl -s http://localhost:11434/api/version

# 反映させるにはサービスごと再起動
brew services restart ollama
```

`brew services restart ollama`後、`/api/version`が`0.32.14`を返すことを確認。その後Pi・Claude Codeの両方で複数ターンの会話を試したところ、`system message`エラーは再発しなかった。

---

## qwen3.8: Auto mode下での重いコーディングタスクに新たな課題（2026-08-17追記）

`system message`バグ修正後、実際にコード生成タスク（マンデルブロ集合・テトリスの新規スクリプト作成）を試したところ、以下のエラーが**Pi・Claude Codeの両方で再現**した。

```
qwen3.8:27b-mlx is temporarily unavailable (timed out), so auto mode cannot determine the safety of Bash right now.
```

**原因**: Auto modeはBashコマンドを実行する前に「安全かどうか」をモデル自身に問い合わせて判定する。Ollamaのllama-serverは`-np 1`（同時1リクエストのみ）で動作するため、進行中の重いメイン生成（大きなプロンプトのプリフィル等）の後ろに安全性判定リクエストが並ぶ形になり、待ちきれずタイムアウトする。

実測したプリフィル速度は**約100〜115 tok/s**。nemotron-3.5-lightningの約850〜1,080 tok/sと比べて1/8以下であり、`qwen3.8`が**Dense構造（27.78B全パラメータ活性化）**である以上、当マニュアル既出の知見（muse-glimmer比較: Dense構造はMoEより実計算量が桁違いに大きく遅い）とそのまま一致する。

Pi・Claude Codeという独立した2つのハーネス双方で同一の現象が再現したことから、特定ツール固有の不具合ではなく、**qwen3.8のDense構造＋Ollamaの直列処理（`-np 1`）という構造的な制約**と判断できる。

**ただし**、qwen3.8・nemotron-3.5-lightningのどちらも、**ファイル作成からGitHubへのpushまでの一連の操作自体は問題なく完走できることを確認した**。Auto modeの安全性判定タイムアウトは「少し待って再試行」すれば通ることが多く、致命的な機能不全ではない。

### 2026-08-17時点の最終まとめ

| モデル | 互換性 | プリフィル速度 | Auto mode下の実運用 | ファイル作成〜git push | 総合評価 |
|---|---|---|---|---|---|
| `qwen3.6:35b-mlx` / `qwen3.6:27b-mlx` | ◎ エラー0件 | ◎ | ◎ 問題なし | ◎ 問題なし | 引き続き最有力 |
| `qwen3.8:27b-mlx` | ◎ v0.32.14で修正済み（要`brew services restart`） | △ 約100〜115 tok/s（Dense構造のため遅い） | △ 安全性判定タイムアウトが頻発（再試行で通る） | ◎ 問題なし | バグは解消したが速度面で本命には及ばない |
| `nemotron-3.5-lightning:30b-mlx` | ◎ エラー0件 | ◎ 約850〜1,080 tok/s | △ 5分タイムアウトが頻発 | ◎ 問題なし | 互換性・プリフィルは良好だがデコード側に課題 |

**総括**: `qwen3.6`系は今回の検証を通じても最も安定して実用的だった。`qwen3.8`はリリース直後の`system message`バグはv0.32.14で解消したが、Dense構造による処理速度の遅さがAuto mode運用時の障壁になっている。`nemotron-3.5-lightning`は互換性・プリフィル速度は優秀だが、デコード側のタイムアウトが引き続き課題。いずれのモデルも、ファイル作成・git pushという基本的なエージェントタスク自体は完走できており、致命的な機能欠如があるわけではない。

---

## 【重要】ツール呼び出しを排除すればハングは解消する（stock_analysisでの検証・2026-08-26追記）

`stock_analysis`プロジェクトで、本マニュアルの知見（Dense構造の遅さ・Auto modeの安全性判定タイムアウト・`-np 1`直列処理）を裏付ける決定的な検証結果が得られたため、ここに記録する。詳細は[stock-monitoring.md](stock-monitoring.md)・[stock_analysisのllm_comparison.md](../../../stock_analysis/llm_comparison.md)を参照。

### 背景

`stock_analysis`では2026-05-25・2026-08-25の2回、`claude` CLI + `ANTHROPIC_BASE_URL=Ollama`（本マニュアルと同じ、Claude CodeのAuto mode下でローカルモデルにBash/Read/Write等のツール呼び出しをさせる方式）で、`qwen3.8:27b`・`qwen3.6:27b-mlx`・`gemma4:31b-mlx`・`muse-glimmer:30b`の4モデルがいずれも7分〜23分でハング（無応答）した。この時点では「27B〜35B級モデルはこのMacのハードウェアでエージェント的用途に使うこと自体が無理」と結論づけていた。

### 検証: ツール呼び出しを完全に排除したら何が起きるか

2026-08-26、`scripts/local/`という新しい実行方式を構築した。要点:

- **ローカルLLMにツール呼び出しを一切させない**（Bash/Read/Write/WebFetch等のtool_calls機能を使わない）
- データ収集・ファイル保存・git操作はすべてPython/Bashスクリプト側が行う
- ローカルLLMには、Ollamaの`/v1/chat/completions`エンドポイントへ**1回のPOSTリクエスト**で「収集済みデータを渡してテキストを生成させる」ことだけを依頼する（`local_agent/scripts/batch_call.py`を使用。本マニュアルとは異なりClaude Code自体を介さない）

同一プロンプト規模（約5,000〜11,000文字の企業分析データ＋出力指示）で、上記4モデル全てを再テストしたところ、**全モデルが完走した**：

| モデル | 旧方式（Auto mode・ツール呼び出しあり） | 新方式（ツール呼び出しなし・直接API） |
|---|---|---|
| `qwen3.8:27b` | ❌ 20分51秒でハング | ✅ 518秒（約8.6分）で完走 |
| `qwen3.6:27b-mlx` | ❌ 7分26秒でハング | ✅ 844秒（約14分）で完走 |
| `gemma4:31b-mlx` | ❌ 23分16秒でハング | ✅ 461秒（約7.7分）で完走 |
| `muse-glimmer:30b` | ❌ 8分経過で中止 | ✅ 385秒（約6.4分）で完走 |

### 結論：原因は「モデルが遅い」ではなく「ツール呼び出しの直列処理」

本マニュアルの「qwen3.8: Auto mode下での重いコーディングタスクに新たな課題」の節で既に述べた通り、Ollamaのllama-serverは`-np 1`（同時1リクエストのみ）で動作するため、Auto mode下では**メイン生成リクエストの後ろに安全性判定・ツール呼び出しの逐次リクエストが並び、待ちきれず5分タイムアウトする**。今回の結果は、この構造的制約を裏付けている：

- ツール呼び出し（＝複数回のリクエスト往復、うち安全性判定はメイン生成の完了を待って割り込む）がある限り、Dense構造で遅いモデル（qwen3.8・muse-glimmer・gemma4）は`-np 1`の直列待ち行列に詰まってタイムアウトし続ける
- ツール呼び出しを排除して**1回のリクエストで完結**させれば、同じモデルでも「遅いが確実に完走する」（385〜844秒）状態に戻る。これは`nemotron-3.5-lightning`の非Dense（Hybrid MoE）構造が示す速さには及ばないが、実用範囲内である

**実務上の含意**: Claude Code / Pi のようなエージェントハーネス経由でローカルモデルにツール呼び出しをさせる用途（本マニュアルの主要な使い方）では、依然として`qwen3.6`系のようなMoE構造の軽量モデルが有利。一方、**「大きなコンテキストを渡してレポート・記事・分析文を1回で生成させる」用途**（stock_analysisの`scripts/local/`、`rakuten_margin`の週次戦略生成等）では、ツール呼び出しを使わない設計に切り替えることで、Dense構造の重いモデルも含めて選択肢が大きく広がる。この場合の品質評価（NTT分析での比較）は以下の通り：

| モデル | 品質（主観） | 特記事項 |
|---|---|---|
| `gemma4:31b-mlx` | ◎ 最も網羅的 | フレームワーク全構成・DCF計算・競合比較まで自発的に出力。他言語混入なし |
| `muse-glimmer:30b` | ◎ 最も素直 | データ欠損を正直に申告。他言語混入なし。**stock_analysisはこれをプライマリに採用** |
| `qwen3.8:27b` | ◎ 最も詳細 | データ矛盾を自ら検知・注記。中国語・韓国語の単語が1〜2箇所混入 |
| `nemotron-3.5-lightning:30b` | ○ 情報量少なめ | 最速（168秒）。**stock_analysisはこれをフォールバックに採用** |
| `qwen3.6:27b-mlx` | △ 可読性低い | 数値を漢数字化・専門用語をカタカナ音写化（「PER」→「パー」等）し実用上読みにくい |

---

## コード生成 × ツール呼び出しの実測比較を公開（2026-08-26追記）

`code_gen_bench/` の結果を1枚のページにまとめて GitHub Pages で公開した。

**<https://masauehr.github.io/local_agent/>** — 「ローカルLLM実測比較」（`docs/index.html`、GitHub Pages は `docs/` を配信）

対象は `ornith-1.5:35b` / `gemma4:31b-mlx` / `qwen3.6:35b-mlx` / `qwen3.8:27b-mlx` / `nemotron-3.5-lightning:30b-mlx` の5機種。
易・中・難のコード生成課題（生成物を subprocess 実行して判定）と、Claude Code 経由の
「バグ修正 → テスト実行 → git commit」エージェントタスクの両方を実測した。ページ掲載の主な数値:

| 指標 | ornith-1.5:35b | nemotron-3.5-lightning:30b-mlx | qwen3.6:35b-mlx |
|---|---|---|---|
| コード生成 平均時間 | **26.1秒（最速、qwen3.6の約3倍速）** | 80.4秒 | 88.9秒 |
| コード生成 PASS率 | 3/3 | 3/3 | 単発でタイポ由来の実行時エラーあり |
| ツール呼び出しエージェント 完走時間 | **158.5秒（最速）** | 291.5秒 | 完走（安定） |
| エージェントタスク | PASS（8ターン） | PASS（8ターン） | PASS |
| 総括での位置付け | 「生成速度・エージェント安定性ともに最有力」 | 「実績重視・手堅い選択肢」（コードブロック二重ネストの癖に後処理側で注意） | エージェント用途は健在、単発生成の信頼性はやや後退 |

要点は callout の一文「**コード生成単体の比較と、エージェントとしての比較は別物だった**」。
`qwen3.8:27b-mlx` はコード生成品質だけなら上位だが、Claude Code 経由のマルチターンは15分タイムアウトで唯一未完走（Dense構造の低速という既出知見どおり）。

再現用リポジトリ: [code_gen_bench/](https://github.com/masauehr/local_agent/tree/main/code_gen_bench)（`prompts/` `results/` `logs/` `tool_call_bench/` `verify.py` `run_bench.py` `run_tool_bench.py`）

---

## weather_digest / ai_news でのツール呼び出しエージェント実運用（2026-08-28追記）

上記の実測比較を踏まえ、`ornith-1.5:35b` と `nemotron-3.5-lightning:30b-mlx` を、**Claude Code / Pi を介さず
Ollama の `/api/chat` tool-calling を直接回すループ**（各プロジェクト固有の `local_agent.py`）で
週次まとめ記事を生成するエージェントとして2つの本番自動化に組み込んだ。

| プロジェクト | 位置付け | 保存先 | launchd 実行時刻（日/曜） |
|---|---|---|---|
| `weather_digest` | secondary エンジン（`local_agent.py --slug ornith / nemotron`）。qwen3.6・Claude Haiku と合わせて4モデル比較、Claude Sonnet が評価ページを自動生成 | `articles/ornith_weekly/` `articles/nemotron_weekly/` | 日曜 ornith 09:30 / nemotron 10:30（qwen 08:00・Haiku 12:00 の間） |
| `ai_news` | variant サブモデル（`local_agent.py --variant ornith / nemotron`）。README・index 更新と月次生成は行わず記事生成と push のみ | `articles/weekly_ornith_2/` `articles/weekly_nemotron/` | 土曜 ornith 10:00 / nemotron 11:00 |

どちらも「自分の記事ファイルと専用アーカイブ一覧だけを更新し、README・トップ index は触らない」設計。

### weather_digest 先行テスト実行の結果（2026-08-28、週 `0828`）

launchd の初回稼働（次の日曜）を待たず `run_weather_ornith.sh` / `run_weather_nemotron.sh` を手動実行:

| モデル | 生成記事 | サイズ | トピック数 | 所要（ターン数） | 結果 |
|---|---|---|---|---|---|
| `ornith-1.5:35b` | `articles/ornith_weekly/2026-0828.md` | 約9.6 KB | 7 | 約2分（12ターン） | 記事生成〜git push まで完走 |
| `nemotron-3.5-lightning:30b-mlx` | `articles/nemotron_weekly/2026-0828.md` | 約4.0 KB | 8 | 約3分（16ターン） | 記事生成〜git push まで完走 |

- **Auto mode のデコード5分タイムアウトは発生しなかった。** 本節冒頭のとおりこの用途は Claude Code の Auto mode を経由せず、安全性判定リクエストがメイン生成に割り込む `-np 1` 直列待ちが起きないため、2026-08-16 検証で `nemotron` に見られた「デコード5分タイムアウト頻発」はこの構成では再現しない。
- `nemotron` は公開ページ・過去節の所見どおり `ornith` より情報量が少なめで、今回の出力では出典 URL に実在しない形式（`https://news.web.nhk/...` 等）が数件混じっていた。weather_digest 側では比較ページ＋Sonnet 評価で可視化される想定。
- ai_news 側にも同週（`2026-0828`）の ornith / nemotron 記事が生成済み。

### 用途別の使い分け（本マニュアルの整理の更新）

| 用途 | 推奨 | 根拠 |
|---|---|---|
| Claude Code / Pi 経由でツール呼び出しをさせる（Auto mode） | `qwen3.6` 系（MoE軽量） | `-np 1` 直列処理下で Dense 低速モデルは安全性判定タイムアウトが頻発（既出） |
| 各プロジェクト固有の tool-calling ループを直接回す（Auto mode なし） | `qwen3.6` / `ornith-1.5` / `nemotron-3.5-lightning` いずれも実用 | weather_digest / ai_news で記事生成〜push まで完走を確認（本節） |
| 大きなコンテキストを渡して1回で生成させる（ツール呼び出しなし） | Dense 含め選択肢が広い（`gemma4` `muse-glimmer` `qwen3.8` 等） | stock_analysis の検証（前節） |
