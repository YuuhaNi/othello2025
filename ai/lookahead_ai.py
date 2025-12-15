"""
先読みAI (Lookahead AI)
2手先を読んで最善手を選ぶAI

自分の手 → 相手の最善手 を予測して、最終的に自分に有利な手を選ぶ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from othello import can_place_x_y, move_stone, copy

def count_stones(board, stone):
    """
    指定した色の石の数を数える

    Args:
        board: 盤面
        stone: 石の色 (1: 黒, 2: 白)

    Returns:
        石の数
    """
    count = 0
    for row in board:
        count += row.count(stone)
    return count

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

def evaluate_board(board, my_stone):
    """
    盤面を評価する（シンプルに石の数の差）

    Args:
        board: 盤面
        my_stone: 自分の石の色

    Returns:
        評価値（自分の石数 - 相手の石数）
    """
    opponent = 3 - my_stone
    my_count = count_stones(board, my_stone)
    opp_count = count_stones(board, opponent)
    return my_count - opp_count

def lookahead_2(board, stone):
    """
    2手先を読んで最善手を選ぶ

    1. 自分の全ての合法手を試す
    2. それぞれの手について、相手の最善手（相手にとって最も有利）を予測
    3. 相手が最善手を打った後の盤面を評価
    4. 自分にとって最も有利な手を選ぶ

    Args:
        board: 盤面
        stone: 自分の石の色

    Returns:
        (x, y): 選択した手
    """
    my_moves = get_valid_moves(board, stone)

    if not my_moves:
        return None

    opponent = 3 - stone
    best_move = None
    best_score = float('-inf')

    # 自分の各手を試す
    for my_x, my_y in my_moves:
        # 自分の手を打った後の盤面をシミュレート
        temp_board = copy(board)
        move_stone(temp_board, stone, my_x, my_y)

        # 相手の合法手を取得
        opponent_moves = get_valid_moves(temp_board, opponent)

        if not opponent_moves:
            # 相手が打てない場合、この盤面の評価値をそのまま使う
            score = evaluate_board(temp_board, stone)
        else:
            # 相手の最善手を予測（相手にとって最も有利 = 自分にとって最悪）
            worst_score = float('inf')

            for opp_x, opp_y in opponent_moves:
                # 相手の手を打った後の盤面をシミュレート
                temp_board2 = copy(temp_board)
                move_stone(temp_board2, opponent, opp_x, opp_y)

                # この盤面を評価
                score = evaluate_board(temp_board2, stone)

                # 相手にとって最善（自分にとって最悪）
                if score < worst_score:
                    worst_score = score

            score = worst_score

        # 自分にとって最善の手を選ぶ
        if score > best_score:
            best_score = score
            best_move = (my_x, my_y)

    return best_move

class LookaheadAI:
    """2手先読みAIクラス"""

    def face(self):
        return "🔮"  # 水晶玉（未来を見る）

    def place(self, board, stone):
        return lookahead_2(board, stone)

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

    ai = LookaheadAI()
    print(f"先読みAI: {ai.face()}")

    # 黒(1)の手を選択
    x, y = ai.place(test_board, 1)
    print(f"選択した手: ({x}, {y})")
