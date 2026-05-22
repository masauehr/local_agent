#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テトリスゲームのPython実装
"""

import curses
import random
import time

# ブロックの形状（I, O, T, S, Z, J, Lの7種類）
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]

# 色の定義
COLORS = [
    curses.COLOR_CYAN,    # I
    curses.COLOR_YELLOW,  # O
    curses.COLOR_MAGENTA, # T
    curses.COLOR_GREEN,   # S
    curses.COLOR_RED,     # Z
    curses.COLOR_BLUE,    # J
    curses.COLOR_WHITE,   # L
]

class TetrisGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        self.stdscr.keypad(1)
        self.stdscr.timeout(100)

        # ゲーム領域の設定
        self.height = 20
        self.width = 10
        self.game_area = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # スコア
        self.score = 0

        # 現在のブロック
        self.current_shape = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0

        # 次のブロック
        self.next_shape = None
        self.next_color = None

        # ゲームオーバー
        self.game_over = False

        # 初期化
        self.new_block()

    def new_block(self):
        """新しいブロックを生成する"""
        if self.next_shape is None:
            self.next_shape, self.next_color = random.choice(list(zip(SHAPES, COLORS)))

        self.current_shape = self.next_shape
        self.current_color = self.next_color
        self.current_x = self.width // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        # 次のブロックを準備
        self.next_shape, self.next_color = random.choice(list(zip(SHAPES, COLORS)))

        # 重なりチェック
        if self.check_collision():
            self.game_over = True

    def check_collision(self):
        """衝突チェック"""
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    if (self.current_y + y >= self.height or
                        self.current_x + x < 0 or
                        self.current_x + x >= self.width or
                        self.game_area[self.current_y + y][self.current_x + x]):
                        return True
        return False

    def rotate(self):
        """ブロックを回転させる"""
        # 回転前の形状を保存
        old_shape = self.current_shape

        # 回転（行と列を入れ替え、行を逆順にする）
        self.current_shape = [[self.current_shape[y][x] for y in range(len(self.current_shape))]
                              for x in range(len(self.current_shape[0]) - 1, -1, -1)]

        # 衝突チェック
        if self.check_collision():
            self.current_shape = old_shape

    def move(self, dx, dy):
        """ブロックを移動させる"""
        self.current_x += dx
        self.current_y += dy

        if self.check_collision():
            self.current_x -= dx
            self.current_y -= dy
            return False
        return True

    def drop(self):
        """ブロックを落とす"""
        while self.move(0, 1):
            pass

    def lock_block(self):
        """ブロックを固定する"""
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.game_area[self.current_y + y][self.current_x + x] = self.current_color

        # ラインクリアチェック
        self.clear_lines()

        # 新しいブロックを生成
        self.new_block()

    def clear_lines(self):
        """埋まったラインをクリアする"""
        lines_cleared = 0
        for y in range(self.height):
            if all(self.game_area[y]):
                # ラインを削除
                del self.game_area[y]
                self.game_area.insert(0, [0 for _ in range(self.width)])
                lines_cleared += 1

        # スコア計算
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 700
        elif lines_cleared == 4:
            self.score += 1500

    def draw(self):
        """ゲーム画面を描画する"""
        self.stdscr.clear()

        # ゲーム領域を描画
        for y in range(self.height):
            for x in range(self.width):
                if self.game_area[y][x]:
                    self.stdscr.addch(y, x, '■', curses.color_pair(self.game_area[y][x]))

        # 現在のブロックを描画
        if not self.game_over:
            for y, row in enumerate(self.current_shape):
                for x, cell in enumerate(row):
                    if cell:
                        self.stdscr.addch(self.current_y + y, self.current_x + x, '■',
                                        curses.color_pair(self.current_color))

        # 次のブロックを描画
        next_x = self.width + 2
        next_y = 2
        for y, row in enumerate(self.next_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.stdscr.addch(next_y + y, next_x + x, '■', curses.color_pair(self.next_color))

        # スコアを表示
        self.stdscr.addstr(0, self.width + 2, f"Score: {self.score}")

        # ゲームオーバー表示
        if self.game_over:
            self.stdscr.addstr(self.height // 2, self.width // 2 - 5, "GAME OVER", curses.A_BOLD)

        self.stdscr.refresh()

    def run(self):
        """ゲームを実行する"""
        last_time = time.time()

        while not self.game_over:
            current_time = time.time()

            # 定期的にブロックを下に移動
            if current_time - last_time > 0.5:
                if not self.move(0, 1):
                    self.lock_block()
                last_time = current_time

            # キー入力を処理
            key = self.stdscr.getch()
            if key == curses.KEY_LEFT:
                self.move(-1, 0)
            elif key == curses.KEY_RIGHT:
                self.move(1, 0)
            elif key == curses.KEY_DOWN:
                self.move(0, 1)
            elif key == curses.KEY_UP:
                self.rotate()
            elif key == ord(' '):
                self.drop()
            elif key == ord('q'):
                break

            self.draw()

        # ゲーム終了
        self.stdscr.nodelay(0)
        self.stdscr.getch()

def main(stdscr):
    """メイン関数"""
    # カラーを初期化
    curses.start_color()
    for i, color in enumerate(COLORS):
        curses.init_pair(i + 1, color, curses.COLOR_BLACK)

    # ゲームを作成して実行
    game = TetrisGame(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)
