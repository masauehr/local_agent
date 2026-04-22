# ローカルLLMエージェント（local_agent）セットアップ・操作マニュアル

## クイックスタート（エイリアス登録済みの場合）

```bash
lagent    # Ollama + gemma4:e2b で起動
bllama    # Bonsai-8B（llama-server）で起動 ※事前に llama-server の起動が必要
```

> エイリアスは `~/.bash_profile` に登録済み。詳細は[エイリアス設定セクション](#エイリアス設定lagent--bllama)を参照。

> **注意**: `lagent` だけで起動してもスキルは読み込まれない。スキルは起動時に `--skill` で指定する必要がある。チャット中に「スキルを読んで」と言っても、AIが `read_file` でファイルを読むだけで、**システムプロンプトには反映されない**（効果が弱い）。

```bash
lagent --skill git_commit_push   # スキルを指定して起動
```

---

## 概要

ローカルLLM（Ollama / llama.cpp）に**スキル**（タスク特化のMarkdownファイル）を与えて、回答品質・フォーマット・言語制御を向上させる仕組みを実験・改善するプロジェクト。ファイル操作・git操作を自然言語で実行できるエージェント機能も実装済み。

- **プロジェクトディレクトリ**: `~/projects/local_agent/`
- **LLMサーバー**: Ollama（`http://localhost:11434`）または llama-server（`http://localhost:8080`）
- **推奨モデル**: `gemma4:e2b`（Ollama・ツール安定）/ `Bonsai-8B`（llama-server・超軽量）
- **Python仮想環境**: `.venv/`

---

## ディレクトリ構成

```
local_agent/
├── start.sh            # Claude Code をローカルLLMで起動するメインスクリプト
├── setup/
│   └── install.sh      # 初回セットアップ（Ollama確認・モデルDL・venv作成）
├── scripts/
│   ├── agent.py        # インタラクティブエージェント（ツール呼び出し対応）
│   └── skill_loader.py # スキルファイル読み込みユーティリティ
├── skills/             # スキルファイル（LLMへの専門指示書）
│   ├── tech_writing_ja.md  # 技術文書作成スキル
│   ├── code_review.md      # コードレビュースキル
│   ├── debug_helper.md     # デバッグ支援スキル
│   ├── commit_message.md   # コミットメッセージ生成スキル
│   ├── regex_explainer.md  # 正規表現解説・生成スキル
│   ├── template.md         # 新規スキル作成テンプレート
│   └── README.md           # スキルの書き方ガイド
├── examples/
│   ├── basic_chat.py       # 基本チャットサンプル（ストリーミング対応）
│   ├── tool_use_test.py    # ツール呼び出し動作確認
│   └── compare_skills.py   # スキルあり・なしの回答を並べて比較
├── CLAUDE.md           # Claude Code向け指示
└── README.md           # プロジェクト概要
```

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
3. デフォルトモデル（`qwen2.5:1.5b`）のダウンロード
4. Python 仮想環境（`.venv/`）の作成と `openai` パッケージのインストール

---

## エイリアス設定（`lagent` / `bllama`）

どのディレクトリからでも短いコマンドで起動できるよう、エイリアスを設定している。

### 現在の設定場所

**`~/.bash_profile`**（当初 `.zshrc` に設定していたが `.bash_profile` に移行）

```bash
# ローカルLLMエージェント（Ollama / gemma4:e2b）
alias lagent='cd ~/projects/local_agent && source .venv/bin/activate && python3 scripts/agent.py'

# Bonsai-8B エージェント（llama-server / ポート8080）
alias bllama='cd ~/projects/local_agent && source .venv/bin/activate && OLLAMA_BASE_URL=http://localhost:8080/v1 OLLAMA_MODEL=bonsai-8b python3 scripts/agent.py'
```

### 使い方

```bash
# Ollama（gemma4:e2b）で起動
lagent

# Bonsai-8B（llama-server）で起動（事前に llama-server の起動が必要）
bllama
```

### 移行の経緯

- 当初 `~/.zshrc` にエイリアスを登録していた
- ターミナル環境の都合により `~/.bash_profile` に移行

> **注意**: `.bash_profile` の変更を反映するには `source ~/.bash_profile` または新しいターミナルタブを開く。

---

## 通常の起動手順

### Claude Code をローカルLLMで起動（メイン）

```bash
cd ~/projects/local_agent

# デフォルトモデル（qwen2.5:1.5b）で起動
./start.sh

# モデルを指定して起動
./start.sh phi4-mini:latest
./start.sh qwen2.5-coder:7b
```

`start.sh` が自動で行うこと：
- Ollama サーバーの起動確認（未起動なら自動起動）
- `ANTHROPIC_BASE_URL=http://localhost:11434` の設定
- `ANTHROPIC_API_KEY=ollama` の設定
- 指定モデルで `claude` コマンドを起動

> **注意**: 起動時に「Do you want to use this API key?」と聞かれたら **「2. No (recommended)」** を選ぶ。

### Python エージェントを直接起動

```bash
cd ~/projects/local_agent
source .venv/bin/activate
python3 scripts/agent.py

# モデルを変更する場合
OLLAMA_MODEL=phi4-mini:latest python3 scripts/agent.py
```

---

## 使用中のモデル一覧

| モデル | サイズ | 特徴 | 起動コマンド |
|--------|--------|------|-------------|
| `qwen2.5:1.5b` | 1.0GB | 軽量・汎用・日本語対応（デフォルト） | `./start.sh` |
| `phi4-mini:latest` | 2.5GB | バランス型 | `./start.sh phi4-mini:latest` |
| `qwen2.5-coder:7b` | 4.7GB | コード特化・高精度 | `./start.sh qwen2.5-coder:7b` |
| `qwen2.5:7b` | 4.7GB | 汎用7Bモデル | `OLLAMA_MODEL=qwen2.5:7b python3 scripts/agent.py` |
| `gemma4:e2b` | 5.1GB | Google製・**ツール呼び出しが最も安定**（推奨） | `OLLAMA_MODEL=gemma4:e2b python3 scripts/agent.py` |
| `deepseek-coder:1.3b` | 0.8GB | 軽量・コード特化 | `OLLAMA_MODEL=deepseek-coder:1.3b python3 scripts/agent.py` |

### モデルのツール呼び出し対応状況（実験結果）

| モデル | ツール呼び出し | 日本語品質 | 備考 |
|--------|--------------|-----------|------|
| `gemma4:e2b` | ◎ 安定 | ◎ | **agent.py のデフォルト** |
| `qwen2.5:7b` | △ 不安定 | △ 中国語漏れあり | システムプロンプトで言語指定が必要 |
| `deepseek-coder:1.3b` | 未確認 | — | — |

### モデルの追加ダウンロード

```bash
ollama pull <モデル名>
# 例
ollama pull qwen2.5-coder:1.5b
```

---

## 動作確認

```bash
# Ollamaサーバーの確認
curl http://localhost:11434/api/tags

# ダウンロード済みモデルの確認
ollama list

# コマンドラインで直接テスト
ollama run qwen2.5:1.5b "Pythonでfizzbuzzを書いて"

# Pythonスクリプトで確認
source .venv/bin/activate
python3 examples/basic_chat.py
```

---

## モデル名のルール

- バージョンタグ付き: `qwen2.5:1.5b`、`qwen2.5-coder:7b` → そのまま使う
- バージョンタグなし: `phi4-mini` → `phi4-mini:latest` と指定する

```bash
# 正しい例
MODEL="${1:-qwen2.5:1.5b}"      # バージョンタグあり
MODEL="${1:-phi4-mini:latest}"  # バージョンタグなし

# 誤った例
MODEL="${1:-qwen2.5:1.5b:latest}"  # :latest は不要
```

---

---

## スキル機能

スキルとは**LLMへの専門指示書（Markdownファイル）**。システムプロンプトとして渡すことで、ローカルLLMでも特定タスクの回答品質・フォーマットを向上させられる。

### スキル一覧

| スキル名 | ファイル | 効果 |
|---------|---------|------|
| `tech_writing_ja` | skills/tech_writing_ja.md | 技術文書を「一言・詳細・具体例・注意点」の構造で出力 |
| `code_review` | skills/code_review.md | コードを「重大な問題→改善提案→良い点→修正後のコード」で整理 |
| `debug_helper` | skills/debug_helper.md | エラーから「種類→原因→修正方法→確認手順」を提示 |
| `commit_message` | skills/commit_message.md | diffから `feat/fix/refactor` 等のprefixつきコミットメッセージを生成 |
| `regex_explainer` | skills/regex_explainer.md | 正規表現を解説・生成・デバッグ。パーツ表・マッチ例つき |
| `git_commit_push` | skills/git_commit_push.md | status→add→commit→push を全自動実行。各ステップの確認・メッセージ自動生成 |

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
python3 examples/compare_skills.py gemma4:e2b tech_writing_ja "DNSとは何ですか"
python3 examples/compare_skills.py gemma4:e2b code_review "以下のコードをレビューして。def f(x): return eval(x)"
```

### スキル実験の知見

- スキルにより**フォーマット・構造化・過剰提案の抑制**が改善される
- `qwen2.5:7b` はスキルなしだと中国語漏れが頻発。スキルに `## 言語ルール` セクションを追加すると改善
- スキルは「言語制御」としても機能する（スキルなしでは制御できない）

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
| OpenAI API標準（`tool_calls`） | `gemma4:e2b` | そのまま処理 |
| `<tool_call>` タグ形式（テキスト） | `qwen2.5:7b` 等 | フォールバックパーサーで処理 |

`gemma4:e2b` はOpenAI API標準形式で安定してツール呼び出しができるため**推奨**。

### デバッグモード

ツール呼び出しがうまくいかない場合は `AGENT_DEBUG=1` で生の出力を確認できる：

```bash
AGENT_DEBUG=1 python3 scripts/agent.py
# [DEBUG] tool_calls=... content=... が表示される
```

---

## トラブルシュート

### `ModuleNotFoundError: No module named 'openai'`
仮想環境が有効化されていない。

```bash
source .venv/bin/activate
```

### Claude Code がローカルに接続できない
環境変数が設定されていない。`./start.sh` を使って起動するか、手動で設定：

```bash
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama
claude --model qwen2.5:1.5b
```

### モデルが見つからないエラー
`ollama list` でモデル名を確認し、正確なタグを指定する。

### Ollama サーバーが起動しない

```bash
pkill ollama   # 既存プロセスを終了
ollama serve   # 再起動
```

### 生成が遅い・不安定
- メモリ不足の可能性 → Activity Monitor でメモリ圧迫を確認
- より軽いモデルに切り替え（`qwen2.5:1.5b` など）

---

## Bonsai 8B（1ビット量子化LLM）agent.py 連携テスト結果

### テスト概要（2026-04-21実施）

Bonsai-8B（Qwen3ベース・1ビット量子化・**1.1GB**）を llama-server で起動し、`agent.py` から接続してツール呼び出しを検証。

### 起動手順

```bash
# llama-server 起動（bonsai-demo に llama-server バイナリ・GGUFモデルあり）
cd ~/projects/1bit_LLM/bonsai-demo
./scripts/start_llama_server.sh &   # ポート8080で起動

# agent.py を Bonsai に向けて起動
cd ~/projects/local_agent
source .venv/bin/activate
OLLAMA_BASE_URL=http://localhost:8080/v1 OLLAMA_MODEL=bonsai-8b python3 scripts/agent.py
```

### テスト結果

| テスト内容 | 結果 | 備考 |
|-----------|------|------|
| `list_files` | ✓ 正常 | ツール呼び出し・日本語回答ともに問題なし |
| `write_file` | ✓ 正常 | ファイル作成・保存成功 |
| `run_git status` | ✓ 正常 | 正確な結果を日本語で整形して返答 |
| `run_git add .` | ✓ 正常 | ステージング成功 |
| add → commit 連続呼び出し | △ 不安定 | commitツールを呼ばずに成功を捏造するケースあり |

### Bonsai vs gemma4:e2b 比較

| 項目 | Bonsai-8B | gemma4:e2b |
|------|-----------|-----------|
| モデルサイズ | **1.1GB** | 5.1GB |
| バックエンド | llama-server | Ollama |
| 単発ツール呼び出し | ○ 安定 | ◎ 安定 |
| ツール連鎖（add→commit等） | △ 途中で捏造あり | ◎ 安定 |
| 日本語品質 | ○ 良好 | ◎ 良好 |
| **推奨用途** | メモリ節約優先・単発操作 | git連携など連続操作 |

### 注意点

- コミット等の連続操作は1ステップずつ指示する方が確実
  - 「git add . して」→完了確認→「feat: XXX でコミットして」
- ツールを呼ばず結果を捏造することがあるため、重要操作後は `git status` で確認推奨
- コンテキストサイズは `CTX_SIZE_DEFAULT=8192`（`common.sh` で設定済み）

---

## git_commit_push スキルの実験結果（2026-04-22）

### 目的

「全部やって」の一言で status → add → commit → push まで全自動実行させる `git_commit_push` スキルを作成・検証。

### 試行結果

| ステップ | 動作 | 備考 |
|---------|------|------|
| `list_files` でスキル探索 | ✓ | 自律的にスキルを読みに行く |
| `git status` | ✓ | 正常 |
| `git add` | △ | `git add .` でなく個別ファイルになることがある |
| `git status`（add後確認） | ✓ | スキルの指示通り |
| `git commit` | ✓ | メッセージを自動生成 |
| `git push` | ✗ | ステップ上限（5回）に達して到達できなかった |

### 判明した問題と対処

| 問題 | 対処 | 状態 |
|------|------|------|
| `push` 前にリポジトリを聞き返す | システムプロンプトに push の例を追記 | ✓ 解消 |
| `git add` がスキップされる | スキルに「addをスキップ禁止」を明記 | ✓ 改善 |
| 「追加して」が `read_file` に解釈される | システムプロンプトに `git add` の例を追記 | ✓ 解消 |
| ステップ上限（5回）でpush前に終了 | `run_turn` の上限を5→10に変更 | ✓ 修正済み |
| `git add .` でなく個別ファイルのみ | スキルの指示が弱い | △ 未解決 |

### 教訓

- **多段ツール連鎖はモデル依存**: Bonsai-8B では5〜6ステップが限界。`gemma4:e2b` の方が安定
- **スキルはステップの順番と禁止事項を明示する必要がある**: 「〜しないこと」の記述が重要
- **「全部やって」は現時点では不安定**: 1ステップずつ指示した方が確実
- **pushが空振りしても成功と報告される**: `git push` は「nothing to push」でもエラーにならない

### 確実に動く操作手順（推奨）

```
[あなた] git statusを確認して
[あなた] git add . して
[あなた] 状態を確認して（Changesが出ていることを確認）
[あなた] 「feat: XXX」でコミットして
[あなた] pushして
```

---

## git スキル追加実験（2026-04-23）

### 試みたこと

- `git_commit_push` スキルをさらに改善（「今すぐツールを呼び出す」明記・68行→14行に簡略化）
- 1ステップ専用スキル4つを新規作成（`git_status` / `git_add` / `git_commit` / `git_push`）
- `agent.py` のデフォルトモデルを `gemma4:e2b` → `Bonsai-8B`（llama-server / ポート8080）に変更

### テスト結果まとめ

| テスト | 条件 | 結果 |
|---|---|---|
| 全自動（長文スキル） | `git_commit_push`（68行版） | 全操作を1コマンドにまとめ→捏造 |
| 全自動（修正後） | `git_commit_push`（「今すぐ呼び出す」追記） | 各ステップ個別実行→成功（pushのみリモート未設定で失敗） |
| 全自動（簡略版） | `git_commit_push`（14行版） | 変更なし状態で `log` のみ呼び、ステップ1〜5を捏造 |
| 1ステップ専用 | `git_commit` スキル | `run_git(["commit"])` を `-m` なしで呼びタイムアウト |

### 結論

- **Bonsai-8B での全自動 git 操作は実用レベルに達していない**（実験終了）
- 1ビット量子化モデルは長い指示を読み飛ばし、ツールを呼ばずに架空の出力を捏造する
- スキルを短くしても・1ステップに絞っても、根本的な指示追従の弱さは解消されない
- 多段ツール連鎖には `gemma4:e2b` 等の高性能モデルが必要

### 追加されたスキル

| スキル名 | 内容 |
|---|---|
| `git_status` | status のみ実行・表示 |
| `git_add` | add . → status 確認 |
| `git_commit` | status 確認 → commit（`-m` 必須を明記） |
| `git_push` | push → log 確認 |

---

## Bonsai 8B（1ビット量子化LLM）+ Continue.dev + MCPサーバー連携

### 概要

Bonsai 8B（Qwen3ベース・1ビット量子化・1.1GB）は Tool Calling に対応しており、
Continue.dev 経由でMCPサーバーと連携できる。

```
VS Code (Continue.dev) ← → llama-server (port 8080) ← Bonsai 8B
                       ← → MCP Server (server.py)  ← JMA API
```

### Continue.dev への設定

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

### llama-server の起動

```bash
cd ~/projects/1bit_LLM/bonsai-demo
./scripts/start_llama_server.sh
```

### メモリ不足で起動失敗する場合（8GB MacBook）

デフォルトの `-c 0`（自動）はコンテキスト65536でKVキャッシュ9216MiBを要求し、
8GBマシンでは起動不可。`common.sh` の `CTX_SIZE_DEFAULT` を変更する：

```sh
# ~/projects/1bit_LLM/bonsai-demo/scripts/common.sh
CTX_SIZE_DEFAULT=8192   # 0（自動）から変更
```

メモリ使用量の目安（8192コンテキスト時）:

| 用途 | サイズ |
|------|--------|
| モデル weights | 1,099 MiB |
| KV キャッシュ | 1,152 MiB |
| compute buffer | ~304 MiB |
| **合計** | **~2,555 MiB** ← 5,460 MiB 空きに収まる |

### ローカルLLMでのMCP利用の注意点

| 項目 | 内容 |
|------|------|
| **同時実行禁止** | llama-server は並列リクエスト非対応。Continue と他CLIを同時に使わない |
| **コンテキスト制限** | 8192トークンのため、長い会話後はツール結果が上限を超えやすい |
| **エリアコードの型** | LLMが整数で渡す場合あり。jma-mcp の server.py は `str()` 変換・`anyOf` スキーマで対応済み |
| **ツール選択の精度** | 「沖縄の最高気温」のような地域絞り込みは `get_mdrr_data` を使うよう誘導が必要 |
| **長い出力は苦手** | Bonsai 8B は100行超の生成でハルシネーションが増える |
