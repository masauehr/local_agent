class GameOfLife:
    def __init__(self, width: int, height: int, alive_cells: set[tuple[int, int]]):
        # グリッドのサイズと、初期で生存しているセルの保存
        self.width = width
        self.height = height
        self.alive = set(alive_cells)

    def step(self) -> None:
        # 次世代の生存候補として、生存セル周囲のマスを集める
        candidates = set()
        for (x, y) in self.alive:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        candidates.add((nx, ny))
        # 各候補セルについて生存数に従って次世代の生存セルを決定
        new_alive = set()
        for (x, y) in candidates:
            neighbors = sum(1
                            for dx in (-1, 0, 1)
                            for dy in (-1, 0, 1)
                            if (dx, dy) != (0, 0) and (x + dx, y + dy) in self.alive)
            if neighbors == 3 or (neighbors == 2 and (x, y) in self.alive):
                new_alive.add((x, y))
        self.alive = new_alive

    def render(self) -> str:
        # 各 y 行について ASCII アートを生成し、行末に改行を加えて結合
        lines = []
        for y in range(self.height):
            row = ''.join('#' if (x, y) in self.alive else '.' for x in range(self.width))
            lines.append(row + '\n')
        return ''.join(lines)


if __name__ == "__main__":
    # 幅15×高さ10のグリッドにグライダーを配置
    game = GameOfLife(15, 10, {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)})
    # 世代0から世代4まで、各世代の描画後に step を呼ぶ
    for generation in range(5):
        print(f"Generation {generation}")
        print(game.render())
        game.step()
