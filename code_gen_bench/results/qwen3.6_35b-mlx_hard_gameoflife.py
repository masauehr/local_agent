class GameOfLife:
    def __init__(self, width: int, height: int, alive_cells: set[tuple[int, int]]):
        self.width = width
        self.height = height
        self._alive = set(alive_cells)

    def step(self) -> None:
        next_alive = set()
        # グリッド全体を走査して次の世代の生起セルを計算
        for y in range(self.height):
            for x in range(self.width):
                live_neighbors = 0
                # 隣接8マスの生存数をカウント
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        # 座標範囲外または死んでいるセルはカウントしない（外側は死んでいる仕様）
                        if (nx, ny) in self._alive:
                            live_neighbors += 1

                # ライフルゲームのルール適用
                if (x, y) in self._alive:
                    if live_neighbors in (2, 3):
                        next_alive.add((x, y))
                else:
                    if live_neighbors == 3:
                        next_alive.add((x, y))
        self._alive = next_alive

    def render(self) -> str:
        rows = []
        # 各y座標ごに行を生成し、行末に改行を含める
        for y in range(self.height):
            row_chars = ['#' if (x, y) in self._alive else '.' for x in range(self.width)]
            rows.append(''.join(row_chars) + '\n')
        return ''.join(rows)

if __name__ == "__main__":
    # 幅15×高さ10のグリッドを作成し、指定された初期パターンを配置
    game = GameOfLife(15, 10, {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)})

    # 世代0を表示
    print("Generation 0")
    print(game.render())

    # 世代1から4まで進め、順に出力
    for i in range(1, 5):
        game.step()
        print(f"Generation {i}")
        print(game.render())
