# ローカルLLM 調査まとめ（Mac / Apple Silicon 向け）

> 調査日: 2026-05-22  
> 環境: MacBook Pro / Apple Silicon / 64GB ユニファイドメモリ

---

## 1. ローカルLLM の主なツール比較

| ツール | フォーマット | APIフォーマット | Claude Code互換 | 速度（Apple Silicon） |
|--------|------------|---------------|----------------|----------------------|
| **Ollama** | GGUF / MLX | Anthropic互換 ✅ | ✅ `ollama launch claude` で直接起動 | MLX で最速 |
| **LM Studio** | GGUF | OpenAI互換のみ | ❌ プロキシ必要 | Metal で高速 |
| **mlx_lm** | MLX専用 | OpenAI互換のみ | ❌ プロキシ必要 | **最速**（Unified Memory最適化） |

---

## 2. HuggingFace モデルを Ollama で使う

Ollama は HuggingFace の GGUF モデルを直接ダウンロード・実行できる。Modelfile 不要。

```bash
# HuggingFace から直接実行
ollama run hf.co/{username}/{repository}

# 量子化を指定する例
ollama run hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:IQ3_M

# 70B 級の例（64GB Mac で動作）
ollama run hf.co/bartowski/Qwen2.5-72B-Instruct-GGUF:Q4_K_M
```

参考記事: https://note.com/schroneko/n/n6a7c34f0a50c

---

## 3. メモリ別モデルサイズ目安（Q4_K_M 量子化）

| モデルサイズ | 必要メモリ目安 | 64GB での評価 |
|------------|-------------|-------------|
| 7〜8B | ~5GB | 余裕すぎる |
| 14B | ~9GB | 余裕 |
| 32B | ~20GB | 快適 |
| 70B | ~43GB | **おすすめ・ギリ動く** |
| 72B | ~45GB | ほぼ同上 |

64GB なら **32B〜70B 級**が現実的な選択肢。

---

## 4. MLX について

### MLX とは
Apple が開発した Apple Silicon 向けの機械学習フレームワーク。Unified Memory アーキテクチャを最大限に活用するため、GGUF + Metal より**推論が速い**ことが多い。

### HuggingFace での探し方
- Libraries フィルターで `mlx` を選択
- `mlx-community` という organization が最も充実

### mlx_lm の使い方

```bash
pip install mlx-lm

# 直接実行
mlx_lm.generate --model mlx-community/Qwen2.5-32B-Instruct-4bit --prompt "こんにちは"

# API サーバーとして起動（OpenAI互換 / localhost:8080）
mlx_lm.server --model mlx-community/Qwen2.5-32B-Instruct-4bit
```

### MLX を Claude Code で使う場合（複雑・非推奨）

```bash
# mlx_lm サーバー → LiteLLM プロキシ → Claude Code の順に立てる
pip install litellm
litellm --model openai/qwen --api_base http://localhost:8080/v1 --port 4000

export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=dummy
claude --model qwen
```

LiteLLM の Anthropic 互換エンドポイントは不安定なため、**Claude Code には Ollama 経由を推奨**。

---

## 5. Ollama のモデル種別（`-mlx` と `-cloud`）

Ollama のモデルには **ローカル実行** と **クラウド経由** の2種類がある。

### `-mlx` と `-cloud` の違い

| タグ | SIZE表示 | 実行場所 | 課金 |
|------|---------|---------|------|
| `qwen3.6:35b-mlx` | 21GB など実サイズ | **ローカル**（MLX / Apple Silicon最適化） | なし |
| `gemma4:31b-mlx` | 20GB | **ローカル**（同上） | なし |
| `qwen3.5:397b-cloud` | `-`（ファイルなし） | **クラウド API 経由** | **課金あり** |
| `gemma4:31b-cloud` | `-`（ファイルなし） | **クラウド API 経由** | **課金あり** |

SIZE が `-` のモデルはローカルにファイルが存在せず Ollama がクラウドへ中継する。  
`ollama launch claude` 起動時に表示される `API Usage Billing` は `-cloud` モデル使用時に課金対象となる。

### 注意：nvfp4 量子化は Mac に不向き

| 量子化 | 特徴 | Mac での評価 |
|--------|------|------------|
| Q4_K_M | 汎用 GGUF | ✅ Metal で最適動作 |
| MLX（-mlx タグ） | Apple Silicon 最適化 | ✅ **最速** |
| nvfp4 | NVIDIA FP4 向け | ⚠️ Apple Silicon 非ネイティブ・速度低下の可能性 |

---

## 6. Qwen3.6（2025年5月時点の最新世代）

### 特徴
- **MoE（Mixture of Experts）構造**: 35B 総パラメータだが推論時は 3B のみ活性化
- 速い・メモリ効率が良い・高性能の三拍子
- Vision / Tools / Thinking 対応
- 262K トークンのネイティブコンテキスト

### 性能比較

| モデル | 世代 | パラメータ | 必要メモリ | 推論速度 | 総合評価 |
|--------|------|----------|----------|---------|---------|
| Qwen2.5-72B (GGUF) | 旧世代 | 72B（全活性） | ~43GB | 遅い | 旧世代の大モデル |
| Qwen3-32B (MLX) | 新世代 | 32B（全活性） | ~20GB | 速い | Qwen2.5-72B 同等以上 |
| **Qwen3.6-35B (MoE)** | **最新世代** | **35B総計/3B活性** | **~20GB** | **速い** | **最もおすすめ** |

### 使い方

```bash
# モデルを取得
ollama pull qwen3.6:35b-mlx

# Claude Code を直接起動（Ollama 公式の方法）
ollama launch claude --model qwen3.6:35b-mlx

# 従来の手動方法（環境変数を自分で設定）
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=ollama
claude --model qwen3.6:35b-mlx
```

> `ollama launch claude` は Ollama の公式機能。環境変数の設定を自動で行い Claude Code を起動する。  
> `-mlx` タグ付きモデルを指定することでローカル MLX 実行になり課金されない。

### ローカルモデルが使われているか確認する方法

```bash
# Claude Code 内で確認
/status
```

設定画面でベースURLが `http://localhost:11434` になっていれば Ollama 経由のローカル実行。  
`api.anthropic.com` になっていれば本番 API に接続されているので課金対象。

---

## 7. Continue（VS Code 拡張）での使い方

Continue は OpenAI 互換 API を直接サポートするため、Ollama・LM Studio・mlx_lm すべてと連携できる。

```json
// ~/.continue/config.json
{
  "models": [
    {
      "title": "Qwen3.6-35B (Ollama)",
      "provider": "ollama",
      "model": "qwen3.6:35b"
    },
    {
      "title": "Qwen3.6 (MLX直接)",
      "provider": "openai",
      "model": "qwen3.6",
      "apiBase": "http://localhost:8080/v1",
      "apiKey": "dummy"
    }
  ]
}
```

---

## 8. RakutenAI-2.0-8x7B-instruct（日本語チャット用）

### 概要

| 項目 | 内容 |
|------|------|
| 開発元 | 楽天 |
| アーキテクチャ | MoE 8×7B（総47Bパラメータ） |
| ベースモデル | Mistral-7B-v0.1 |
| 言語 | 日本語・英語 |
| ライセンス | Apache 2.0（商用利用可） |
| フォーマット | GGUF のみ（MLX 非対応） |

### 量子化・サイズ（64GB Mac での評価）

| 量子化 | サイズ | 64GB Mac | 備考 |
|--------|-------|----------|------|
| IQ2_XXS | 12.6GB | ✅ | 品質は落ちる |
| Q4_K_M | 28.5GB | ✅ | バランス型 |
| Q6_K | 38.5GB | ✅ | 高品質 |
| **Q8_0** | **49GB** | **✅** | **ほぼ原版精度** |

### インストール（Ollama 経由）

```bash
# Q8_0（ほぼ原版精度・64GB Mac 推奨）
ollama pull hf.co/mmnga/RakutenAI-2.0-8x7B-instruct-gguf:Q8_0

# チャットで使う
ollama run hf.co/mmnga/RakutenAI-2.0-8x7B-instruct-gguf:Q8_0
```

### 実験結果（2026-05-22）

#### RakutenAI / qwen3.6 / gemma4 の3モデル比較

| 評価項目 | RakutenAI Q4_K_M | qwen3.6:35b-mlx | gemma4:31b-mlx |
|---------|-----------------|-----------------|----------------|
| **日本語の自然さ** | ◎ 最も自然 | △ 英語が混じる | △ 英語の思考過程が表示されて煩わしい |
| **知識の正確さ** | ✅ 正確 | ✅ 正確 | ✅ 正確 |
| **論理的思考** | ❌ 間違えた | ✅ 正しい | ✅ 正しい |
| **コード生成** | ❌ 拒否 | ○ 可能 | ◎ qwenより良い印象 |
| **日本語文章の修正** | ◎ 期待できる | 未評価 | 未評価 |
| **AIエージェント適性** | ❌ ツール非対応 | ✅ 十分 | ◎ より良い可能性 |
| **速度** | ✅ 速い | ✅ 速い | 未評価 |
| **Claude Code 使用** | ❌ ツール非対応 | ✅ 対応 | △ コード生成◎だがファイル書き出しでハング |

#### 用途別推奨モデル

| 用途 | 推奨モデル | 理由 |
|------|-----------|------|
| Claude Code / AIエージェント | `gemma4:31b-mlx` | ツール対応・コード生成◎ |
| Claude Code（安定稼働重視） | `qwen3.6:35b-mlx` | 実績あり・安定 |
| 日本語チャット・文章校正 | `RakutenAI Q4_K_M` or `Q8_0` | 日本語の自然さが最良 |

#### Claude Code（AIエージェント）での追加評価

- **qwen3.6:35b-mlx**: コード修正に失敗する傾向あり、バグを解消できないケースがあった。論理的思考は向上しているが、コード生成能力は qwen3.5 からあまり改善していない印象
- **gemma4:31b-mlx**（Ollama アップデート後に評価）:
  - テトリスゲームの Python コードを生成 → **一応動くコードを生成できた** ✅
  - `.py` ファイルや Jupyter Notebook への書き出し命令で **ハングアップ** ❌（ファイル書き込みツールの呼び出しが正しく動作しない）
  - コードをチャット上で生成する能力は十分だが、Claude Code のツール（Write/Edit）との連携が不安定
- gemma4:31b-mlx は Ollama 0.20.2 で `unsupported architecture` エラー → Ollama アップデートで解消
- **devstral-small-2:24b**: テトリスコード生成は可能だがファイル保存に時間がかかりすぎ、性能も gemma4 より劣る。**実用的ではない**
- qwen3.6 / gemma4 はコンテキスト内に英語が混入する傾向あり（日本語チャット用途では気になる）
- RakutenAI は論理推論・コード生成が弱く、Claude Code での利用不可（ツール非対応）

#### Claude Code 実用評価まとめ（2026-05-22時点）

現時点では**どのローカルモデルも Claude Code での実用レベルには達していない**。

| モデル | コード生成 | ファイル書き出し | 総合評価 |
|--------|-----------|---------------|---------|
| `gemma4:31b-mlx` | ✅ 動くコードを生成 | ❌ ハングアップ | 最も期待できるが不安定 |
| `qwen3.6:35b-mlx` | △ バグ解消できないケースあり | ✅ 動作する | ツール連携は安定するが品質不足 |
| `devstral-small-2:24b` | △ 生成できるが遅い | ❌ 非常に遅い | 実用的でない |
| `RakutenAI` | ❌ 拒否 | ❌ ツール非対応 | Claude Code 不可 |

---

## 9. 64GB Mac 向け推奨構成まとめ

| 目的 | 推奨構成 |
|------|---------|
| **Claude Code（現時点で最もマシ）** | `qwen3.6:35b-mlx`（ツール連携が最も安定） |
| **日本語チャット・文章校正** | `RakutenAI Q4_K_M` or `Q8_0` |
| **超大型モデルを試す** | `-cloud` タグ（397B など）← 課金に注意 |
| **Continue で使う** | Ollama プロバイダーとして設定 |

### 起動コマンド

```bash
# Claude Code をローカルモデルで起動
ollama launch claude --model qwen3.6:35b-mlx    # 現時点で最安定

# 日本語チャット（ollama run で直接対話）
ollama run hf.co/mmnga/RakutenAI-2.0-8x7B-instruct-gguf:Q4_K_M
```

### 結論（2026-05-22 実験完了）
- **ローカルLLMでの Claude Code 実用はまだ困難**。コード生成はできても、ファイル書き出し・バグ修正・多段ツール連携が不安定
- `qwen3.6:35b-mlx` がツール連携の安定性では現時点で最良
- `gemma4:31b-mlx` はコード生成力があるが Write/Edit ツールでハングする
- `devstral-small-2:24b` はファイル保存が遅すぎて実用的でない
- `RakutenAI` は日本語チャット専用として割り切る
- `-mlx` タグ = ローカル MLX 実行（無料・Apple Silicon 最適化・課金なし）
- `-cloud` タグ = クラウド API 経由（課金あり・`API Usage Billing` 表示）
