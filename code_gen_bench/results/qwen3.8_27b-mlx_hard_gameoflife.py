import sys


class GameOfLife:
    """コンウェイのライフゲームのシミュレータ"""

    def __init__(self, width: int, height: int, alive_cells: set[tuple[int, int]]):
        self.width = width
        self.height = height
        # 生きているセルの集合として内部状態を保持
        self.alive: set[tuple[int, int]] = set(alive_cells)

    def _count_neighbors(self, x: int, y: int) -> int:
        """(x, y) の隣接8マスで生存しているセル数を返す。
        グリッド外は死んでいるものとして扱う。"""
        count = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                # 端の外側は全て死んでいる
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) in self.alive:
                        count += 1
        return count

    def step(self) -> None:
        """現在の状態を次の世代に更新する（インプレース）"""
        # 変化が起きうるセルを集める（生存セルとその隣接セル）
        candidates: set[tuple[int, int]] = set()
        for (x, y) in self.alive:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        candidates.add((nx, ny))

        next_alive: set[tuple[int, int]] = set()
        for (x, y) in candidates:
            n = self._count_neighbors(x, y)
            is_alive = (x, y) in self.alive
            if is_alive:
                # 生存条件：隣接生存数が2または3
                if n == 2 or n == 3:
                    next_alive.add((x, y))
            else:
                # 誕生条件：隣接生存数がちょうど3
                if n == 3:
                    next_alive.add((x, y))

        self.alive = next_alive

    def render(self) -> str:
        """現在のグリッドをASCII文字列で返す。
        生存セルは'#'、死亡セルは'.'。各行末に改行を付与する。"""
        lines: list[str] = []
        for y in range(self.height):
            row = "#".join([""] * (self.width + 1))  # 先に単純作成
            # 各xを確認して文字列を構築
            chars: list[str] = []
            for x in range(self.width):
                if (x, y) in self.alive:
                    chars.append("#")
                else:
                    chars.append(".")
            lines.append("".join(chars) + "\n")
        return "".join(lines)


if __name__ == "__main__":
    # 幅15×高さ10のグリッドにグライダーを配置
    glider: set[tuple[int, int]] = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    game = GameOfLife(width=15, height=10, alive_cells=glider)

    # 世代0を表示
    print("Generation 0")
    sys.stdout.write(game.render())

    # 世代1〜4を表示（各世代の前にstepを呼び出す）
    for gen in range(1, 5):
        game.step()
        print(f"Generation {gen}")
        sys.stdout.write(game.render())
