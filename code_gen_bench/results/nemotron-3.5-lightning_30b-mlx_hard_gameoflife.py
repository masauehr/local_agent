class GameOfLife:
    """コンウェイのライフゲーム"""

    def __init__(self, width: int, height: int, alive_cells: set[tuple[int, int]]):
        self.width = width
        self.height = height
        self.alive = set(alive_cells)

    def step(self):
        # 次世代の生存セルを決定
        next_alive = set()
        # 候補となるセル（生存セルとその隣接8マス）を収集
        candidates = set()
        for (x, y) in self.alive:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        candidates.add((nx, ny))
        candidates.update(self.alive)

        for (x, y) in candidates:
            # 隣接する生存セルの数を数える
            count = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) in self.alive:
                        count += 1
            if (x, y) in self.alive:
                if count == 2 or count == 3:
                    next_alive.add((x, y))
            else:
                if count == 3:
                    next_alive.add((x, y))
        self.alive = next_alive

    def render(self) -> str:
        output = ""
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if (x, y) in self.alive:
                    row += "#"
                else:
                    row += "."
            row += "\n"
            output += row
        return output


if __name__ == "__main__":
    width, height = 15, 10
    # グライダーの初期配置
    initial_cells = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    game = GameOfLife(width, height, initial_cells)

    for gen in range(5):
        print(f"Generation {gen}")
        print(game.render(), end="")
        if gen < 4:
            game.step()
