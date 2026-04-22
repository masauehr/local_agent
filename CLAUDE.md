# CLAUDE.md — local_agent プロジェクト

## プロジェクト概要

ローカルLLM（Ollama / llama.cpp）に**スキル**（タスク特化のMarkdownファイル）を与えて、回答品質・フォーマット・言語制御を向上させる仕組みを実験・改善するプロジェクト。

あわせて、ファイル操作・git操作を自然言語で実行できるツール呼び出し機能も実装・実験している。

## 技術スタック

- **ローカルLLMサーバー**: Ollama v0.15以降 または llama-server（llama.cpp）
- **推奨モデル**: `gemma4:e2b`（Ollama・ツール呼び出し安定）/ `Bonsai-8B`（llama-server・1.1GB超軽量）
- **言語**: Python 3.10以上
- **APIクライアント**: `openai` パッケージ（OpenAI互換）
- **接続先**: Ollama `http://localhost:11434` / llama-server `http://localhost:8080`

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
│   ├── code_review.md    # コードレビュースキル
│   └── git_commit_push.md # git status→add→commit→push を全自動実行するスキル
└── examples/
    └── compare_skills.py  # スキルあり・なしの回答を並べて比較する実験スクリプト
```

### 実験結果サマリー（2026-04-21）

- スキルによってフォーマット・構造化・中国語漏れ抑制の効果を確認
- `gemma4:e2b` がツール呼び出し・日本語品質ともに最も安定（実験当時）
- `Bonsai-8B` を **現在のデフォルトモデルに設定済み**（llama-server / ポート8080）
- `qwen2.5:7b` はシステムプロンプトで言語ルールを明示しないと中国語が混入する
- `agent.py` に `write_file` / `list_files` / `run_git` ツールを追加済み
- `<tool_call>` テキスト形式フォールバックパーサーを実装済み（モデル非依存）

### git操作スキル実験（2026-04-22）

#### 試みたこと
- `git_commit_push` スキルを作成（status → add → commit → push の全自動フロー）
- `lagent`（Bonsai-8B / llama-server）で「git関連のskillを読んで、pushまで全部やって」と指示

#### 判明した問題と対処

| 問題 | 原因 | 対処 |
|------|------|------|
| `push` 前に確認質問が出る | システムプロンプトに`push`の例がなかった | `agent.py` のシステムプロンプトに例を追記 |
| `git add` がスキップされる | モデルがstepを省略する | スキルに「addをスキップ禁止」を明記・add後のstatus確認を追加 |
| 「追加して」→ `read_file` が呼ばれる | `git add` と `read_file` の区別がつかない | システムプロンプトに `git add` の例を追記 |
| ステップ上限（5回）でpush前に終了 | `run_turn` の上限が低すぎた | 上限を5→10に変更 |
| `git add .` でなく個別ファイルだけaddされる | スキルの指示が弱い | 現在未解決 |

#### 結果
- Bonsai-8B（lagent）での「全自動push」は**現時点では不安定**
- `list_files → status → add → status確認 → commit` まで動くが、pushに至らないことが多い
- 多段ツール連鎖はモデル性能に強く依存する

### git操作スキル追加実験（2026-04-23）

#### 試みたこと
- `agent.py` のデフォルトモデルを `gemma4:e2b` → `Bonsai-8B`（llama-server / ポート8080）に変更
- スキルの大幅簡略化（68行→14行）で Bonsai-8B の指示理解を改善しようとした
- `git_commit_push` を1ステップ専用スキル4つ（`git_status` / `git_add` / `git_commit` / `git_push`）に分割してテスト

#### テスト結果まとめ

| テスト | 条件 | 結果 |
|---|---|---|
| 全自動（スキル修正前） | `git_commit_push`（長文版） | 全操作を1コマンドにまとめて実行→全部捏造 |
| 全自動（スキル修正後） | `git_commit_push`（`今すぐツール呼び出す`追記） | 各ステップ個別実行→成功（pushのみリモート未設定で失敗） |
| 全自動（リモート設定後） | `git_commit_push`（簡略版） | 変更なしの状態で`log`のみ呼び、ステップ1〜5を捏造 |
| 1ステップ専用スキル | `git_status` / `git_add` / `git_commit` | `git commit`を`-m`なしで呼んでタイムアウト |

#### 結論
- **Bonsai-8B での全自動 git 操作は実用レベルに達していない**
- 1ビット量子化モデルは長い指示を読み飛ばし、ツールを呼ばずに架空の出力を捏造する傾向がある
- 多段ツール連鎖は `gemma4:e2b` 等より高性能なモデルが必要
- 1ステップ単純操作（`status` のみ等）なら動作するが、明示的な指示が必要

### 次にやること
- 他のモデル（`gemma4:e2b` 等）でツール呼び出し精度を比較
- エージェントにチャット内容をマニュアルとして保存させる実験

### 起動コマンド
```bash
cd ~/projects/local_agent
source .venv/bin/activate

# デフォルト（Bonsai-8B）※事前に bllama でサーバー起動が必要
python3 scripts/agent.py

# スキルあり
python3 scripts/agent.py --skill tech_writing_ja

# モデル比較実験
python3 examples/compare_skills.py gemma4:e2b tech_writing_ja "DNSとは何ですか"
```
