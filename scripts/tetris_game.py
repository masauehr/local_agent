"""
簡易テトリスゲーム
Python 3.x / Pygame を使用した最小実装
操作:
  ← → : 左右移動
  ↑   : 回転
  ↓   : ソフトドロップ
  Space : ハードドロップ
  P   : ポーズ
  Esc : 終了
"""

import pygame
import random
import sys

# 定数
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = COLS * CELL_SIZE + 200
HEIGHT = ROWS * CELL_SIZE

BG_COLOR = (20, 20, 30)
GRID_COLOR = (60, 60, 80)
TEXT_COLOR = (240, 240, 240)

# 色定義
COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 120),
    "Z": (240, 40, 40),
    "J": (40, 80, 240),
    "L": (240, 160, 40),
}

# テトリミノの形状
SHAPES = {
    "I": [[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]],
    "O": [[[1,1],[1,1]]],
    "T": [[[0,1,0],[1,1,1]]],
    "S": [[[0,1,1],[1,1,0]]],
    "Z": [[[1,1,0],[0,1,1]]],
    "J": [[[1,0,0],[1,1,1]]],
    "L": [[[0,0,1],[1,1,1]]],
}

PIECES = list(SHAPES.keys())


class Piece:
    """テトリミノ"""

    def __init__(self):
        self.kind = random.choice(PIECES)
        self.shape = SHAPES[self.kind][0]
        self.color = COLORS[self.kind]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        """回転処理"""
        # 90度回転
        rotated = [list(row) for row in zip(*self.shape[::-1])]
        return rotated


class Board:
    """ゲームボード"""

    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0

    def can_place(self, piece, x, y, shape):
        """配置可能か判定"""
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    nx, ny = x + j, y + i
                    if nx < 0 or nx >= COLS or ny >= ROWS:
                        return False
                    if ny >= 0 and self.grid[ny][nx]:
                        return False
        return True

    def lock(self, piece):
        """ピースを固定"""
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    ny, nx = piece.y + i, piece.x + j
                    if 0 <= ny < ROWS:
                        self.grid[ny][nx] = piece.color

    def clear_lines(self):
        """ライン消去"""
        new_grid = [row for row in self.grid if not all(row)]
        cleared = ROWS - len(new_grid)
        if cleared:
            self.grid = [[None]*COLS for _ in range(cleared)] + new_grid
            self.score += cleared * 100 * (self.score // 500 + 1)
        return cleared


def draw_board(screen, board):
    screen.fill(BG_COLOR)
    # 盤面描画
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if board.grid[y][x]:
                pygame.draw.rect(screen, board.grid[y][x], rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)


def draw_piece(screen, piece):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((piece.x + j)*CELL_SIZE, (piece.y + i)*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, piece.color, rect)
                pygame.draw.rect(screen, TEXT_COLOR, rect, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)

    board = Board()
    piece = Piece()
    next_piece = Piece()

    drop_time = 0
    fall_speed = 500  # ms

    running = True
    while running:
        dt = clock.tick(60)
        drop_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if board.can_place(piece, piece.x - 1, piece.y, piece.shape):
                        piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if board.can_place(piece, piece.x + 1, piece.y, piece.shape):
                        piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if board.can_place(piece, piece.x, piece.y + 1, piece.shape):
                        piece.y += 1
                        board.score += 1
                elif event.key == pygame.K_UP:
                    rotated = piece.rotate()
                    if board.can_place(piece, piece.x, piece.y, rotated):
                        piece.shape = rotated
                elif event.key == pygame.K_SPACE:
                    # ハードドロップ
                    while board.can_place(piece, piece.x, piece.y + 1, piece.shape):
                        piece.y += 1
                        board.score += 2
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # 自動落下
        if drop_time > fall_speed:
            drop_time = 0
            if board.can_place(piece, piece.x, piece.y + 1, piece.shape):
                piece.y += 1
            else:
                board.lock(piece)
                board.clear_lines()
                piece = next_piece
                next_piece = Piece()

        draw_board(screen, board)
        draw_piece(screen, piece)

        # スコア表示
        score_surf = font.render(f"Score: {board.score}", True, TEXT_COLOR)
        screen.blit(score_surf, (COLS*CELL_SIZE + 20, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
