# 調査メモ: macOS 27 `fm` CLI（Apple on-device Foundation Model）

- 調査日: 2026-09-22
- ステータス: 実機テスト＋ネット記事調査（本居宣長・太陽系の惑星・マンデルブロー集合コードで動作確認済み）

## 概要

- **提供元**: Apple（macOS 27に標準搭載、追加インストール不要）
- **`fm`とは**: Apple Intelligenceを支えるオンデバイス言語モデル（Apple Foundation Models, AFM）にターミナルから直接アクセスできる公式CLI
- **起動方法**: ターミナルで直接起動（Ollama/MLX経由ではない）。今回の検証もこの方法。

## モデル仕様

- **オンデバイスモデル**: 約3Bパラメータ（unified-3b / AFM 3 Core とも呼ばれる）、Apple Neural Engine (ANE) で実行
- **コンテキスト上限**: 4,096トークン（指示＋プロンプト＋回答の合計）
- **自動ルーティング**: 複雑なタスクは自動的にPrivate Cloud Compute（PCC、Appleのクラウド）に切り替わる
- **ハードウェア制約**: 4GBのシステムメモリをANEに固定するため、8〜16GB Macではスワップ問題が起きうる（[iosdev.in](https://www.iosdev.in/articles/fm-cli-macos-27)より）

## コマンド一覧（[Qiita/StayHomeLabNet](https://qiita.com/StayHomeLabNet/items/4b8178717abf23c7022e)より、日本語記事で最も網羅的）

| コマンド | 内容 |
|---|---|
| `fm available` | 利用可能性確認 |
| `fm license` | 利用条件同意管理 |
| `fm respond` | 1回限りの質問応答 |
| `fm chat` | 対話型セッション（`/model`でPCC切替、`/save`で保存・`--resume`で再開） |
| `fm count-tokens` | トークン数確認 |
| `fm schema object` | 構造化出力（JSON）のスキーマ定義 |
| `fm serve` | ローカルAPIサーバー起動（後述） |

主なオプション: `--instructions/-i`（指示）、`--image`+`--text`（画像入力＋質問）、`--tool ocr/barcode`（OCR・バーコード読取）、`--use-case content-tagging`（分類最適化）

## 実機テストの結果

| 課題 | 結果 |
|---|---|
| 太陽系の惑星に関する質問 | 正確に回答 |
| 本居宣長についての質問 | **複数のハルシネーション**。生没年（実際は1730–1801年→「1641–1701」と誤答）、肩書き（実際は国学者だが「儒学者」と誤記。本居宣長は儒教批判で知られる人物）、代表作『古事記伝』の完成年（実際は1798年→「1701年」と誤答）。文体は整っているが核心的事実が軒並み誤り |
| マンデルブロー集合のPythonコード生成 | 生成できず |

**考察**: Apple公式（WWDC26 Session 334）も「オンデバイスモデルはテキスト要約・抽出・分類向けで、コード生成・数学計算・高度な推論には非対応」と明言しており、今回の結果は仕様通り。一般常識（学習データに大量出現する情報）は答えられるが、専門的な人物史のような細部は自信満々に誤情報を生成する典型的なハルシネーションパターン。他の検証者からも同種の報告あり（バージョン情報の矛盾回答、架空の手順生成など、[mac.install.guide](https://mac.install.guide/terminal/fm-command)）。

## OllamaやClaude Codeからの呼び出しについて

- **`fm serve`が公式で存在**: `http://localhost:8000/v1/` でOpenAI Chat Completions互換のローカルAPIサーバーを起動できる（Apple純正機能）。Ollama互換・Anthropic Messages API互換のエンドポイントはApple自身は提供していない。
- **Ollama連携**: 非公式のサードパーティOSS（`olleh`、`appllama`、`afm-Server`、`osaurus`、`FMProxy`）が`fm serve`のOpenAI互換出力をOllama API形式に変換するブリッジとして複数存在。数日で複数登場するなどコミュニティの関心は高い。
- **Claude Code連携**: **非対応**。Claude Codeは`ANTHROPIC_BASE_URL`にAnthropic Messages API互換のエンドポイントを要求するが、`fm serve`はOpenAI形式のみ。見つかった`ClaudeForFoundationModels`（Anthropic製）は逆方向の統合で、「Apple純正の`LanguageModelSession` APIを使うSwiftアプリ側でオンデバイスモデルの代わりにクラウドのClaudeを呼べるようにする」ものであり、Claude Code側からfmのオンデバイスモデルを呼ぶ仕組みではない。繋ぐには自前でOpenAI→Anthropic変換プロキシ（litellm等）が必要で、実績のある方法は確認できなかった。

## 発展性の評価

`fm serve`が公式でOpenAI互換APIを提供している時点でエコシステムとの接続基盤は強く、コミュニティのOllamaブリッジが数日で複数登場するなど関心は高い。ただしモデル自体は3B・4Kコンテキストという制約が変わらないため、「繋がる先が増える」ことと「Claude Codeのような複雑なコーディングエージェント用途で実用になる」ことは別問題。用途はファイル分類・要約・OCR・軽量なツール呼び出しに留め、`local_agent`プロジェクトの主力モデル（`qwen3.6:35b-mlx`等）の置き換えには不向きと判断する。

## 参照元

- https://mac.install.guide/terminal/fm-command
- https://www.iosdev.in/articles/fm-cli-macos-27
- https://developer.apple.com/videos/play/wwdc2026/334/
- https://medium.com/macoclock/apples-fm-is-here-run-apple-foundation-models-from-your-terminal-on-macos-26-no-beta-required-33fa0932f22c
- https://blakecrosley.com/blog/foundation-models-python-fm-cli（英語記事で最も詳しい。CLI+Python SDK+実装パターンまで網羅）
- https://qiita.com/StayHomeLabNet/items/4b8178717abf23c7022e（日本語記事で最も詳しい。コマンド・オプションを網羅したCLIリファレンス）
- https://qiita.com/chibicco/items/ef1a9e40c4cdf15d8e21（ユーザー最初の参考記事。導入寄り）
- https://it-araiguma.com/apple-intelligence-python-sdk-local-ai-development-guide/（Python SDK・商用ライセンス・Ollama共存可否など開発者視点）
- https://gigazine.net/news/20260921-locally-ai-apple-foundation-models/（一般向け）
- fm serve/Ollama連携の非公式ブリッジ例: https://github.com/mattt/olleh 、https://github.com/michaloo/appllama 、https://github.com/Techopolis/afm-Server
