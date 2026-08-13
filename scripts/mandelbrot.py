#!/usr/bin/env python3
"""マンデルブロ集合の描画 - 結果は mandelbrot.png に保存する"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def compute_mandelbrot(x_min, x_max, y_min, y_max, width, height, max_iter):
    """マンデルブロ集合を計算し、イテレーション数配列を返す"""
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y

    Z = np.zeros_like(C, dtype=np.complex128)
    ITER = np.zeros((height, width), dtype=int)

    for i in range(max_iter):
        mask = Z.real ** 2 + Z.imag ** 2 < 4.0  # |Z| < 2
        if not mask.any():
            break
        Z[mask] = Z[mask] ** 2 + C[mask]
        ITER[mask] = i + 1

    return ITER


def main():
    width, height = 1200, 800
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5
    max_iter = 200

    print("マンデルブロ集合を計算中...")
    iters = compute_mandelbrot(x_min, x_max, y_min, y_max, width, height, max_iter)

    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.imshow(
        iters.T,
        extent=[x_min, x_max, y_min, y_max],
        cmap="inferno",
        origin="lower",
    )
    ax.set_title("Mandelbrot Set", fontsize=16)
    ax.set_xlabel("Re")
    ax.set_ylabel("Im")
    ax.axis("off")

    out_path = "mandelbrot.png"
    fig.savefig(out_path, dpi=100, bbox_inches="tight")
    print(f"完了: {out_path} を保存しました")
    plt.close()


if __name__ == "__main__":
    main()
