"""
gemma4
"""
  import pygame
  import random

  # 設定
  SCREEN_WIDTH = 300
  SCREEN_HEIGHT = 600
  BLOCK_SIZE = 30
  GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
  GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

  # 色
  BLACK = (0, 0, 0)
  WHITE = (255, 255, 255)
  GRAY = (128, 128, 128)
  COLORS = [
      (0, 255, 255), # Cyan (I)
      (255, 255, 0), # Yellow (O)
      (128, 0, 128), # Purple (T)
      (0, 255, 0),   # Green (S)
      (255, 165, 0), # Orange (Z)
      (0, 0, 255),   # Blue (J)
      (255, 0, 0),   # Red (L)
  ]

  # テトリミノの形状
  SHAPES = [
      [[1, 1, 1, 1]], # I
      [[1, 1], [1, 1]], # O
      [[0, 1, 0], [1, 1, 1]], # T
      [[0, 1, 1], [1, 1, 0]], # S
      [[1, 1, 0], [0, 1, 1]], # Z
      [[1, 0, 0], [1, 1, 1]], # J
      [[0, 0, 1], [1, 1, 1]], # L
  ]

  class Piece:
      def __init__(self, x, y, shape):
          self.x = x
          self.y = y
          self.shape = shape
          self.color = COLORS[SHAPES.index(shape)]
          self.rotation = 0

      def get_shape(self):
          # 回転処理は簡易化のため形状リストから直接取得（実際には回転行列などで実装）
          return self.shape

  def create_grid():
      return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

  def valid_space(piece, grid):
      shape = piece.get_shape()
      for r, row in enumerate(shape):
          for c, cell in enumerate(row):
              if cell:
                  if (piece.y + r < 0 or piece.y + r >= GRID_HEIGHT or
                      piece.x + c < 0 or piece.x + c >= GRID_WIDTH or
                      grid[piece.y + r][piece.x + c] != BLACK):
                      return False
      return True

  def clear_rows(grid):
      cleared = 0
      for r in range(GRID_HEIGHT - 1, -1, -1):
          if BLACK not in grid[r]:
              cleared += 1
              del grid[r]
              grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
      return cleared

  def draw_grid(screen, grid):
      for r in range(GRID_HEIGHT):
          for c in range(GRID_WIDTH):
              pygame.draw.rect(screen, grid[r][c], (c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
              pygame.draw.rect(screen, GRAY, (c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

  def main():
      pygame.init()
      screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
      pygame.display.set_caption("Tetris")
      clock = pygame.time.Clock()

      grid = create_grid()
      current_piece = Piece(3, 0, random.choice(SHAPES))
      fall_time = 0
      fall_speed = 0.5 # 秒
      score = 0
      game_over = False

      while not game_over:
          fall_time += clock.get_rawtime()
          clock.tick()

          if fall_time / 1000 >= fall_speed:
              fall_time = 0
              current_piece.y += 1
              if not valid_space(current_piece, grid):
                  current_piece.y -= 1
                  for r, row in enumerate(current_piece.get_shape()):
                      for c, cell in enumerate(row):
                          if cell:
                              grid[current_piece.y + r][current_piece.x + c] = current_piece.color

                  score += clear_rows(grid) * 100
                  current_piece = Piece(3, 0, random.choice(SHAPES))
                  if not valid_space(current_piece, grid):
                      game_over = True

          for event in pygame.event.get():
              if event.type == pygame.QUIT:
                  game_over = True
              if event.type == pygame.KEYDOWN:
                  if event.key == pygame.K_LEFT:
                      current_piece.x -= 1
                      if not valid_space(current_piece, grid):
                          current_piece.x += 1
                  if event.key == pygame.K_RIGHT:
                      current_piece.x += 1
                      if not valid_space(current_piece, grid):
                          current_piece.x -= 1
                  if event.key == pygame.K_DOWN:
                      current_piece.y += 1
                      if not valid_space(current_piece, grid):
                          current_piece.y -= 1

          screen.fill(BLACK)
          draw_grid(screen, grid)

          # 現在のピースを描画
          shape = current_piece.get_shape()
          for r, row in enumerate(shape):
              for c, cell in enumerate(row):
                  if cell:
                      pygame.draw.rect(screen, current_piece.color,
                                     ((current_piece.x + c) * BLOCK_SIZE,
                                      (current_piece.y + r) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
              pygame.draw.rect(screen, GRAY, ((current_piece.x + 0) * BLOCK_SIZE, (current_piece.y + 0) *
  BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

          pygame.display.flip()

      pygame.quit()

  if __name__ == "__main__":
      main()