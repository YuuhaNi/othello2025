"""
貪欲AI (Greedy AI)
現在の手で最も多くの石をひっくり返せる手を選ぶ「おバカ」なAI

オセロでは序盤に多く取りすぎると後で不利になることが多いため、
このAIは強くありません。
"""

import sys
import os
# 親ディレクトリをパスに追加してothelloモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from othello import can_place_x_y

def count_flips(board, stone, x, y):
    """
    指定した位置に石を置いたときに、何個の石がひっくり返るかを数える

    Args:
        board: 盤面
        stone: 石の色 (1: 黒, 2: 白)
        x, y: 石を置く位置

    Returns:
        ひっくり返る石の数
    """
    if not can_place_x_y(board, stone, x, y):
        return 0

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    flip_count = 0

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        temp_count = 0

        # 相手の石が続く限りカウント
        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            temp_count += 1
            nx += dx
            ny += dy

        # 自分の石で挟めた場合のみカウントに加える
        if temp_count > 0 and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            flip_count += temp_count

    return flip_count

def greedy_place(board, stone):
    """
    最も多くの石をひっくり返せる手を選ぶ

    Args:
        board: 盤面
        stone: 石の色 (1: 黒, 2: 白)

    Returns:
        (x, y): 選択した手の座標
    """
    best_move = None
    max_flips = -1

    # 全ての位置を調べる
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                flips = count_flips(board, stone, x, y)
                if flips > max_flips:
                    max_flips = flips
                    best_move = (x, y)

    return best_move

class GreedyAI:
    """貪欲AIクラス"""

    def face(self):
        return "🤑"  # お金の顔（貪欲なイメージ）

    def place(self, board, stone):
        return greedy_place(board, stone)

# デバッグ用
if __name__ == "__main__":
    # テスト用の盤面
    test_board = [
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,1,2,0,0],
        [0,0,2,1,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
    ]

    ai = GreedyAI()
    print(f"貪欲AI: {ai.face()}")

    # 黒(1)の手を選択
    x, y = ai.place(test_board, 1)
    flips = count_flips(test_board, 1, x, y)
    print(f"選択した手: ({x}, {y}), ひっくり返る石の数: {flips}")
