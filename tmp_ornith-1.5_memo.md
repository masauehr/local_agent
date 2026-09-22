# 調査メモ: Ornith-1.5（一時メモ）

- 調査日: 2026-08-26
- ステータス: 一時メモ（要精査・未検証情報を含む）

## 概要

- **開発元**: DeepReinforce（`ornith-ai` / `deepreinforce-ai` として Hugging Face・GitHub に公開）
- **Ornithとは**: オープンソースのエージェント型コーディングLLMファミリー。Anthropicとは無関係の第三者プロジェクト。
- ライセンス: MIT（重み公開）

## 系譜

### Ornith-1.0（2026年6月発表）
- コンセプト: 「Self-Scaffolding」。タスクを解くのと同時に、その解法の足場（ツール構成・手順）自体も学習で構築する。
- ベース: Gemma 4 / Qwen 3.5 を後継学習
- サイズ: 9B Dense / 31B Dense / 35B MoE / 397B MoE
- ベンチマーク（自己申告）: Terminal-Bench 2.1で77.5、SWE-Bench Verifiedで82.4 → 「Claude Opus 4.7超え」と主張

### Ornith-1.5（2026年8月発表、今回の調査対象）
- コンセプト: 1.0の自己足場構築をさらに拡張し、「タスク生成」「スキャフォールド構築」「ロールアウト（解答）最適化」の3つを同時に最適化する自己改善ループ。
  - タスク生成: 能力の穴を突くタスクを段階的難易度で自動生成
  - スキャフォールド構築: 指示・ツール・分解戦略などタスク固有の解法を自動構築
  - ソリューション最適化: 強化学習の報酬シグナルでロールアウトを改善
- 固定の人間キュレーションタスクセットに頼らず、モデル自身がカリキュラムを継続拡張するという主張
- サイズ: 9B Dense / 35B MoE / 397B MoE
- コンテキスト長: 256K、テキスト＋画像入力対応
- ベンチマーク（自己申告）: Terminal-Bench 2.1で86.1、DeepSWEで56.0 → 「Claude Opus 4.8相当」と主張

## エージェントとしての利用

- OpenAI互換エンドポイント + tool calling（function call）標準搭載
- `reasoning_content`（思考過程）と`tool_calls`を分離して返すサービングレシピあり
- 対応ランタイム: Ollama、llama.cpp、vLLM、LM Studio
- 対応エージェントCLI/フレームワーク: OpenCode、Hermes Agent、OpenClaw、LangChain、AutoGen、Unsloth Studio（ファインチューニング）

### OpenCode連携の例
```bash
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="EMPTY"
export OPENAI_MODEL="Ornith-1.5"
```
`~/.config/opencode/opencode.json` に `@ai-sdk/openai-compatible` パッケージ経由でプロバイダー登録。

## 注意点・未検証事項

- ベンチマーク数値はすべて開発元（DeepReinforce/Ornith）の自己申告であり、第三者による独立検証は未確認。
- 397Bはデータセンター級GPUが必要、自前ホスティング前提。
- Claude Codeのような公式サポート・検証済み統合ではない。
- 実運用前にライセンス・セキュリティ・tool calling精度を自環境で要検証。

## 参照元

- https://ollama.com/library/ornith-1.5
- https://ornith.ai/ornith_1_5.html
- https://ornith.ai/ornith_1_0.html
- https://huggingface.co/ornith-ai/Ornith-1.5-9B
- https://huggingface.co/ornith-ai/Ornith-1.5-397B
- https://github.com/ornith-ai/Ornith-1
- https://simonwillison.net/2026/Jun/29/ornith/
- https://www.marktechpost.com/2026/06/25/deepreinforce-releases-ornith-1-0-an-open-source-coding-model-family-that-learns-its-own-rl-scaffolds/
- https://medium.com/data-science-in-your-pocket/ornith-1-5-9b-self-improving-llm-for-coding-07a6340922f0
- https://saascity.io/blog/ornith-1-5-self-improving-open-source-llm-2026
