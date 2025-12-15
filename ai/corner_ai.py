"""
角優先AI (Corner AI)
角を最優先で取るAI

オセロでは角は一度取ると絶対にひっくり返されない最強の位置。
角が取れる場合は必ず角を取り、取れない場合は他の手を選ぶ。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from othello import can_place_x_y
import random

def get_corners(board):
    """
    盤面の角の位置を取得

    Args:
        board: 盤面

    Returns:
        角の座標のリスト [(x, y), ...]
    """
    width = len(board[0])
    height = len(board)

    corners = [
        (0, 0),                    # 左上
        (width - 1, 0),            # 右上
        (0, height - 1),           # 左下
        (width - 1, height - 1)    # 右下
    ]

    return corners

def get_valid_moves(board, stone):
    """
    合法手のリストを取得

    Args:
        board: 盤面
        stone: 石の色

    Returns:
        合法手のリスト [(x, y), ...]
    """
    valid_moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                valid_moves.append((x, y))
    return valid_moves

def corner_place(board, stone):
    """
    角優先で手を選ぶ

    1. 角が取れるなら角を取る
    2. 角が取れないなら、ランダムに手を選ぶ

    Args:
        board: 盤面
        stone: 石の色

    Returns:
        (x, y): 選択した手
    """
    corners = get_corners(board)

    # 角が取れるかチェック
    for x, y in corners:
        if can_place_x_y(board, stone, x, y):
            return (x, y)

    # 角が取れない場合は、合法手からランダムに選ぶ
    valid_moves = get_valid_moves(board, stone)

    if valid_moves:
        return random.choice(valid_moves)

    return None

class CornerAI:
    """角優先AIクラス"""

    def face(self):
        return "📐"  # 角度記号（角のイメージ）

    def place(self, board, stone):
        return corner_place(board, stone)

# デバッグ用
if __name__ == "__main__":
    # テスト1: 初期盤面（角は取れない）
    test_board1 = [
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,1,2,0,0],
        [0,0,2,1,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
    ]

    ai = CornerAI()
    print(f"角優先AI: {ai.face()}")
    print("\nテスト1: 初期盤面（角は取れない）")
    x, y = ai.place(test_board1, 1)
    corners = get_corners(test_board1)
    is_corner = (x, y) in corners
    print(f"選択した手: ({x}, {y}), 角?: {is_corner}")

    # テスト2: 角が取れる盤面
    test_board2 = [
        [0,0,0,0,0,2],
        [0,1,1,1,1,2],
        [0,1,1,2,0,2],
        [0,1,2,1,0,2],
        [0,1,0,0,0,2],
        [0,0,0,0,0,0],
    ]

    print("\nテスト2: 右上の角(5,0)が取れる盤面")
    valid_moves = get_valid_moves(test_board2, 1)
    print(f"黒の合法手: {valid_moves}")
    x, y = ai.place(test_board2, 1)
    corners2 = get_corners(test_board2)
    is_corner = (x, y) in corners2
    print(f"選択した手: ({x}, {y}), 角?: {is_corner}")
    if is_corner:
        print("✅ 角を正しく選択しました！")
    else:
        print(f"❌ 角を選択できませんでした。角の位置: {corners2}")
