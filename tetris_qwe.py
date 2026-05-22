"""
Pygame を使用したテトリスゲーム
"""

import pygame
import random
import sys

# ───────────────────────── 定数 ─────────────────────────
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
GRID_SIZE = 30
GRID_COLS = 10
GRID_ROWS = 20
PLAY_X = (SCREEN_WIDTH - GRID_COLS * GRID_SIZE) // 2
PLAY_Y = 50

# 色定義
COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 120),
    "Z": (240, 40, 40),
    "J": (40, 80, 240),
    "L": (240, 160, 40),
    "BG": (30, 30, 50),
    "GRID": (60, 60, 80),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
}

# テトリミノの形状（回転状態を含む）
SHAPES = {
    "I": [
        [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
        [[0,0,1,0],[0,1,1,1],[0,0,0,1],[0,0,0,0]],
        [[0,0,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
        [[0,0,0,0],[1,0,0,0],[1,1,1,0],[0,0,0,0]],
    ],
    "O": [
        [[0,1,0],[0,1,0],[0,0,0]],
        [[0,1,0],[0,1,0],[0,0,0]],
        [[0,1,0],[0,1,0],[0,0,0]],
        [[0,1,0],[0,1,0],[0,0,0]],
    ],
    "T": [
        [[0,1,0],[1,1,1],[0,0,0]],
        [[0,1,0],[0,1,1],[0,1,0]],
        [[0,0,0],[1,1,1],[0,1,0]],
        [[0,1,0],[1,1,0],[0,1,0]],
    ],
    "S": [
        [[0,1,1],[1,1,0],[0,0,0]],
        [[0,1,0],[0,1,1],[0,1,0]],
        [[0,0,0],[0,1,1],[1,1,0]],
        [[0,1,0],[1,1,0],[0,1,0]],
    ],
    "Z": [
        [[1,1,0],[0,1,1],[0,0,0]],
        [[0,1,0],[1,1,1],[0,0,0]],
        [[0,0,0],[1,1,0],[0,1,1]],
        [[0,0,0],[0,1,0],[1,1,1]],
    ],
    "J": [
        [[1,0,0],[1,1,1],[0,0,0]],
        [[0,1,1],[0,1,0],[0,1,0]],
        [[0,0,0],[1,1,1],[0,0,1]],
        [[0,1,0],[0,1,0],[1,1,0]],
    ],
    "L": [
        [[0,0,1],[1,1,1],[0,0,0]],
        [[0,1,0],[0,1,0],[0,1,1]],
        [[0,0,0],[1,1,1],[1,0,0]],
        [[1,1,0],[0,1,0],[0,1,0]],
    ],
}

PIECE_KEYS = list(SHAPES.keys())
# ─────────────────────────── クラス ────────────────────────

class Piece:
    """テトリミノのピース"""

    def __init__(self, piece_type):
        self.piece_type = piece_type
        self.rotation = 0
        self.shape = SHAPES[piece_type][self.rotation]
        self.color = COLORS[piece_type]
        # グリッド中央上部に生成
        self.x = GRID_COLS // 2 - len(self.shape[0]) // 2
        self.y = -1

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        self.shape = SHAPES[self.piece_type][self.rotation]


class Tetris:
    """テトリスゲーム本体"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        """ゲーム状態をリセット"""
        self.grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.pieces_cleared_anims = []  # クリア中のアニメーション
        self.next_piece = Piece(random.choice(PIECE_KEYS))
        self.current_piece = self.spawn_piece()
        self.drop_interval = 500  # ms
        self.last_drop = 0
        self.paused = False

    def spawn_piece(self):
        piece = self.next_piece
        piece.x = GRID_COLS // 2 - len(piece.shape[0]) // 2
        piece.y = -1
        piece.rotation = 0
        piece.shape = SHAPES[piece.piece_type][piece.rotation]
        self.next_piece = Piece(random.choice(PIECE_KEYS))
        # 生成不可能な場合はゲームオーバー
        if not self.can_move(piece, 0, 0):
            self.game_over = True
        return piece

    def can_move(self, piece, dx, dy):
        """移動可能かチェック"""
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    nx = piece.x + j + dx
                    ny = piece.y + i + dy
                    if nx < 0 or nx >= GRID_COLS or ny >= GRID_ROWS:
                        return False
                    if ny >= 0 and self.grid[ny][nx]:
                        return False
        return True

    def lock_piece(self):
        """ピースを固定"""
        piece = self.current_piece
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    ny = piece.y + i
                    nx = piece.x + j
                    if 0 <= ny < GRID_ROWS and 0 <= nx < GRID_COLS:
                        self.grid[ny][nx] = piece.piece_type

    def clear_lines(self):
        """ライン消去"""
        cleared = []
        for i in range(GRID_ROWS):
            if all(self.grid[i]):
                cleared.append(i)
        for line_idx in reversed(cleared):
            self.grid.pop(line_idx)
            self.grid.insert(0, [0] * GRID_COLS)
            self.pieces_cleared_anims.append((self.last_drop, GRID_SIZE * 3))

        if cleared:
            counts = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += counts.get(len(cleared), 0) * self.level
            self.lines += len(cleared)
            self.level = min(15, self.lines // 10 + 1)
            self.drop_interval = max(100, 500 - (self.level - 1) * 30)

        return bool(cleared)

    def hold_line_fade(self, timestamp):
        """ライン消去アニメーションの更新"""
        return [
            (start, dur) for start, dur in self.pieces_cleared_anims
            if timestamp - start < dur
        ]

    def draw_grid(self):
        """ゲーム領域を描画"""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = PLAY_X + col * GRID_SIZE
                y = PLAY_Y + row * GRID_SIZE
                # 背景
                color = COLORS["BG"] if not self.grid[row][col] else COLORS[self.grid[row][col]]
                pygame.draw.rect(self.screen, color, (x, y, GRID_SIZE, GRID_SIZE), 0)
                # グリッド線
                pygame.draw.rect(self.screen, COLORS["GRID"], (x, y, GRID_SIZE, GRID_SIZE), 1)

    def draw_piece(self, piece, offset_x=0, offset_y=0):
        """ピースを描画"""
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x = PLAY_X + (piece.x + j) * GRID_SIZE + offset_x
                    y = PLAY_Y + (piece.y + i) * GRID_SIZE + offset_y
                    pygame.draw.rect(self.screen, piece.color, (x, y, GRID_SIZE, GRID_SIZE), 0)
                    pygame.draw.rect(
                        self.screen, (255, 255, 255),
                        (x, y, GRID_SIZE, GRID_SIZE), 1
                    )

    def draw_ghost(self):
        """ゴースト（落下先）を表示"""
        piece = self.current_piece
        ghost_y = piece.y
        while self.can_move(piece, 0, ghost_y - piece.y + 1):
            ghost_y += 1
        if ghost_y != piece.y:
            for i, row in enumerate(piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        x = PLAY_X + (piece.x + j) * GRID_SIZE
                        y = PLAY_Y + (ghost_y + i) * GRID_SIZE
                        pygame.draw.rect(self.screen, (40, 40, 60), (x, y, GRID_SIZE, GRID_SIZE), 2)

    def draw_next(self):
        """次のピースを表示"""
        text = self.small_font.render("Next", True, COLORS["WHITE"])
        self.screen.blit(text, (PLAY_X + GRID_COLS * GRID_SIZE + 10, PLAY_Y + 50))
        # 次のピースを描画（中央に配置）
        preview_grid = [[0] * 4 for _ in range(4)]
        piece = self.next_piece
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    preview_grid[i][j] = piece.piece_type
        off_x = (4 - len(piece.shape[0])) * GRID_SIZE // 2
        off_y = (4 - len(piece.shape)) * GRID_SIZE // 2
        for i, row in enumerate(preview_grid):
            for j, cell in enumerate(row):
                if cell:
                    x = PLAY_X + GRID_COLS * GRID_SIZE + 10 + j * GRID_SIZE + off_x // 2
                    y = PLAY_Y + 80 + i * GRID_SIZE + off_y // 2
                    pygame.draw.rect(self.screen, piece.color, (x, y, GRID_SIZE, GRID_SIZE), 0)

    def draw_sidebar(self):
        """サイドバー（スコア等）を描画"""
        sx = PLAY_X + GRID_COLS * GRID_SIZE + 10

        def make_text(text_str, y_pos):
            txt = self.small_font.render(text_str, True, COLORS["WHITE"])
            self.screen.blit(txt, (sx, y_pos))

        make_text(f"Score: {self.score}", PLAY_Y + 220)
        make_text(f"Level: {self.level}", PLAY_Y + 260)
        make_text(f"Lines: {self.lines}", PLAY_Y + 300)

        info_y = PLAY_Y + 360
        make_text("[ Controls ]", info_y)
        make_text("← → : Move", info_y + 40)
        make_text("↑ : Rotate", info_y + 65)
        make_text("↓ : Soft Drop", info_y + 90)
        make_text("Space : Hard Drop", info_y + 115)
        make_text("P : Pause", info_y + 140)
        make_text("R : Restart", info_y + 165)

    def draw_hard_drop_line(self):
        """ハードドロップ時のライン表示"""
        piece = self.current_piece
        drop_dist = (GRID_ROWS - 1 - piece.y)
        if drop_dist > 2:
            line_y = PLAY_Y + GRID_ROWS * GRID_SIZE
            pygame.draw.line(
                self.screen, COLORS["WHITE"],
                (PLAY_X, line_y),
                (PLAY_X + GRID_COLS * GRID_SIZE, line_y),
                3
            )

    def draw(self):
        """画面全体を描画"""
        self.screen.fill(COLORS["BG"])
        self.draw_grid()

        if self.game_over:
            self.draw_game_over()
            return

        # ゴースト描画
        self.draw_ghost()

        # 現在ピース描画
        self.draw_piece(self.current_piece)

        # ライン消去アニメーション
        self.pieces_cleared_anims = self.hold_line_fade(pygame.time.get_ticks())

        # サイドバー描画
        self.draw_next()
        self.draw_sidebar()

        # ポーズ表示
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            text = self.font.render("PAUSED", True, COLORS["WHITE"])
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, rect)

        # ゲーム領域の枠線
        pygame.draw.rect(self.screen, COLORS["WHITE"], (PLAY_X - 2, PLAY_Y - 2, GRID_COLS * GRID_SIZE + 4, GRID_ROWS * GRID_SIZE + 4), 2)

    def draw_game_over(self):
        """ゲームオーバー時"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        text = self.font.render("GAME OVER", True, COLORS["WHITE"])
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)
        restart_text = self.small_font.render("Press R to restart", True, COLORS["WHITE"])
        r_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, r_rect)

    def hard_drop(self):
        """瞬間落下"""
        while self.can_move(self.current_piece, 0, 1):
            self.current_piece.y += 1
            self.score += 2
        self.lock_piece()
        self.clear_lines()
        self.current_piece = self.spawn_piece()

    def soft_drop(self):
        """高速落下"""
        if self.can_move(self.current_piece, 0, 1):
            self.current_piece.y += 1
            self.score += 1

    def move(self, dx):
        """左右移動"""
        if self.can_move(self.current_piece, dx, 0):
            self.current_piece.x += dx

    def rotate_piece(self):
        """回転（壁蹴り対応）"""
        orig_rotation = self.current_piece.rotation
        orig_shape = [row[:] for row in self.current_piece.shape]
        self.current_piece.rotate()
        # 壁蹴り: 左右にずらして衝突回避
        for kick in [0, 1, -1, 2, -2]:
            if self.can_move(self.current_piece, kick, 0):
                self.current_piece.x += kick
                return
        # 回転失敗時は元に戻す
        self.current_piece.rotation = orig_rotation
        self.current_piece.shape = orig_shape

    def handle_events(self):
        """入力処理"""
        kpd = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.hard_drop()
                elif event.key == pygame.K_DOWN:
                    self.soft_drop()
                elif event.key == pygame.K_LEFT:
                    self.move(-1)
                elif event.key == pygame.K_RIGHT:
                    self.move(1)
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    if self.game_over:
                        self.reset_game()

        # 継続処理
        if not self.paused and not self.game_over:
            now = pygame.time.get_ticks()
            if now - self.last_drop > self.drop_interval:
                if self.can_move(self.current_piece, 0, 1):
                    self.current_piece.y += 1
                else:
                    self.lock_piece()
                    self.clear_lines()
                    self.current_piece = self.spawn_piece()
                self.last_drop = now

        return True

    def run(self):
        """ゲームメインループ"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    game = Tetris()
    game.run()
