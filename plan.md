local_agent

ローカルLLMでAIエージェント

**MacでOllama + Claude Code風CLIを最短セットアップできます**。環境変数をOllamaのAPIに差し替えることで、Claude CodeをローカルLLMで動かせますが、実用性はモデル次第で限定的です 。[1][2]

## 必要なもの
- Mac (Apple Silicon推奨、16GB以上メモリが目安) 。[2][1]
- Ollama v0.15以降 (Anthropic互換API対応) 。[3][2]
- モデル例: `qwen2.5-coder:7b` (4.7GB、コード向き) 。[1][2]

## 最短セットアップ手順
1. **Ollamaインストール**: https://ollama.com/download/mac からインストーラをダウンロード・インストール。ターミナルで `ollama serve` を実行してサーバー起動 。[4][2][1]
2. **モデルダウンロード**: `ollama pull qwen2.5-coder:7b` (初回は時間がかかる) 。[2][1]
3. **Claude Codeインストール**: `brew install --cask claude-code` (Homebrew未インストールなら先に `brew install` でセットアップ) 。[1][2]
4. **環境変数設定**: ターミナルで以下を実行  
   ```
   export ANTHROPIC_BASE_URL=http://localhost:11434
   export ANTHROPIC_API_KEY=ollama  # 形式上必要
   ```
   またはOllama v0.15以降なら `ollama launch claude --model qwen2.5-coder:7b` で自動設定 。[3][2]
5. **実行**: `claude --model qwen2.5-coder:7b` で起動。プロジェクトディレクトリでコード生成を試す 。[2][1]

## 動作確認例
シンプルな指示「TypeScriptでカウンターコンポーネントを書いて」ならコード出力可能ですが、ツール呼び出しや複雑タスクでJSON出力止まりやハルシネーションが発生します 。[2]
M4 Mac 32GB + 14Bモデルでも57秒かかり不安定 。[2]
Ollama単体 `ollama run qwen2.5-coder:7b "メールバリデーション関数を書け"` なら78 tokens/secで実用的 。[2]

## トラブルシュート
- ツール非対応エラー: ツールサポートモデル(qwen系)に変える 。[2]
- 遅い/不安定: メモリ増強か32B+モデル検討、またはContinue.devなどシンプルツールへ 。[3][2]
- VSCode統合: Claude Code拡張 + Ollama接続でIDE内使用 。[4]

これで無料・ローカルでClaude Code風体験が得られますが、本家Claudeほどの安定性はないので補助用途向きです 。[1][2]

情報源
[1] 【完全無料】Claude CodeをLocal LLMで実行してみる - Zenn https://zenn.dev/urakawa_jinsei/articles/2b707394d6c216
[2] LOCAL-CLI: Free Claude Code alternative — Works with ANY ... https://github.com/orgs/community/discussions/182276
[3] Ollama v0.15 で Claude Code をローカル実行できるか試してみた https://dev.classmethod.jp/articles/claude-code-ollama-local/
[4] How to Setup Claude Code with Ollama in VSCode on Mac/macOS https://www.youtube.com/watch?v=mNHyASeJlwg
[5] How to Install Ollama on macOS + Run It from Terminal https://www.youtube.com/watch?v=dj_PODDpfeo
[6] Free & Local Claude Code Setup - GitHub Gist https://gist.github.com/mohamedaminehamdi/fd90795ba091f8208e3fd5944bcc2a56
[7] Install and Set Up Ollama https://apxml.com/courses/getting-started-local-llms/chapter-4-running-first-local-llm/setting-up-ollama
[8] FREE Local AI Coding FOREVER (Step-by-Step Tutorial) - YouTube https://www.youtube.com/watch?v=Y3oe0QTSJgE
[9] Claude Code × OllamaWindows / macOS でローカルLLMを使う完全 ... https://note.com/zephel01/n/n36ff0e26e2e6
[10] How to Install Ollama on Mac (macOS) | Use Ollama for Running AI Models Locally (2026) https://www.youtube.com/watch?v=ucxtk-jUj6c
[11] Claude Code - Ollama's documentation https://docs.ollama.com/integrations/claude-code
