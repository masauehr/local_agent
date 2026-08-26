import sys

class GameOfLife:
    """コンウェイのライフゲームをシミュレートするクラス"""
    
    def __init__(self, width: int, height: int, alive_cells: set[tuple[int, int]]):
        """
        初期化メソッド
        :param width: グリッドの幅
        :param height: グリッドの高さ
        :param alive_cells: 初期状態で生存しているセルの座標集合 {(x, y), ...}
        """
        self.width = width
        self.height = height
        self.alive_cells = alive_cells

    def step(self):
        """現在の状態から次の世代へ更新する"""
        new_alive_cells = set()
        
        # 全てのセルについて次世代の生死を判定
        for y in range(self.height):
            for x in range(self.width):
                # 周囲8マスの生存数をカウント
                neighbor_count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        # グリッド外は死んでいるものとして扱う
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if (nx, ny) in self.alive_cells:
                                neighbor_count += 1
                
                # ライフゲームのルール適用
                is_alive = (x, y) in self.alive_cells
                if is_alive:
                    # 生存セルは隣接数が2か3のとき生存
                    if neighbor_count == 2 or neighbor_count == 3:
                        new_alive_cells.add((x, y))
                else:
                    # 死滅セルは隣接数がちょうど3のとき誕生
                    if neighbor_count == 3:
                        new_alive_cells.add((x, y))
        
        self.alive_cells = new_alive_cells

    def render(self) -> str:
        """現在のグリッドをASCIIアートで返す"""
        lines = []
        for y in range(self.height):
            row = "".join("#" if (x, y) in self.alive_cells else "." for x in range(self.width))
            lines.append(row)
        # 1行1つのyに対応し、行末に改行を含める
        return "\n".join(lines) + "\n"

if __name__ == "__main__":
    # 仕様に基づいた設定
    width, height = 15, 10
    # グライダーの初期配置
    initial_cells = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    
    game = GameOfLife(width, height, initial_cells)
    
    # 世代0から世代4まで表示
    for gen in range(5):
        print(f"Generation {gen}")
        # render()は末尾に改行を含むため、end=""を指定
        print(game.render(), end="")
        game.step()
