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

## 8. 64GB Mac 向け推奨構成まとめ

| 目的 | 推奨構成 |
|------|---------|
| **Claude Code メイン（最もシンプル）** | `ollama launch claude --model qwen3.6:35b-mlx` |
| **最速・無料** | Ollama の `-mlx` タグモデル（MLX ローカル実行） |
| **超大型モデルを試す** | `-cloud` タグ（397B など）← 課金に注意 |
| **Continue で使う** | Ollama プロバイダーとして設定 |

### 結論
- `ollama launch claude` は Ollama 公式の Claude Code 起動コマンド（環境変数設定不要）
- `-mlx` タグ = ローカル MLX 実行（無料・Apple Silicon 最適化・最速）
- `-cloud` タグ = クラウド API 経由（課金あり・`API Usage Billing` 表示）
- 最新世代（Qwen3.6 MoE）は旧世代大モデルを性能・速度ともに上回る
- `-mlx` モデルを使う限り、Claude Code でも MLX の恩恵を受けられる
