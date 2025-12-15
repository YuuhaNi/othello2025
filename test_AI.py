import time
"""
2手先読みAI (MyAI)
自分の手→相手の手の2手先まで読んで最善手を選ぶAI

アルゴリズム：
1. 自分の全ての合法手を試す
2. 各手について、相手の全ての応手を試す
3. 相手が最善手を打つと仮定して、自分に最も有利な手を選ぶ
"""

try:
    # Colab等で from sakura import othello として使う場合
    from sakura import othello
    can_place_x_y = othello.can_place_x_y
    move_stone = othello.move_stone
    copy = othello.copy
except ImportError:
    # 直接実行する場合
    from othello import can_place_x_y, move_stone, copy

def get_position_score_6x6():
    """6x6盤面の位置評価スコア"""
    return [
        [100, -20,  10,  10, -20, 100],
        [-20, -20,   5,   5, -20, -20],
        [ 10,   5,   1,   1,   5,  10],
        [ 10,   5,   1,   1,   5,  10],
        [-20, -20,   5,   5, -20, -20],
        [100, -20,  10,  10, -20, 100]
    ]

def get_position_score_8x8():
    """8x8盤面の位置評価スコア"""
    return [
        [100, -20,  10,   5,   5,  10, -20, 100],
        [-20, -20,  -5,  -5,  -5,  -5, -20, -20],
        [ 10,  -5,   5,   3,   3,   5,  -5,  10],
        [  5,  -5,   3,   1,   1,   3,  -5,   5],
        [  5,  -5,   3,   1,   1,   3,  -5,   5],
        [ 10,  -5,   5,   3,   3,   5,  -5,  10],
        [-20, -20,  -5,  -5,  -5,  -5, -20, -20],
        [100, -20,  10,   5,   5,  10, -20, 100]
    ]

def get_position_score(board):
    """盤面サイズに応じた位置評価スコアを取得"""
    size = len(board)
    if size == 6:
        return get_position_score_6x6()
    elif size == 8:
        return get_position_score_8x8()
    else:
        return get_position_score_6x6()

def evaluate_board(board, stone):
    """
    盤面を評価する関数

    位置評価スコアの合計値で評価

    Args:
        board: 盤面
        stone: 評価する側の石の色

    Returns:
        評価値（高いほど有利）
    """
    position_scores = get_position_score(board)
    opponent = 3 - stone

    my_score = 0
    opponent_score = 0

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                my_score += position_scores[y][x]
            elif board[y][x] == opponent:
                opponent_score += position_scores[y][x]

    # 自分のスコア - 相手のスコア
    return my_score - opponent_score

def get_valid_moves(board, stone):
    """合法手のリストを取得"""
    valid_moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                valid_moves.append((x, y))
    return valid_moves

def myai(board, stone):
    """
    2手先読みAIのメイン関数

    Args:
        board: 盤面
        stone: 自分の石の色

    Returns:
        (x, y): 選択した手
    """
    valid_moves = get_valid_moves(board, stone)

    if not valid_moves:
        return None

    opponent = 3 - stone
    best_move = None
    best_score = float('-inf')

    # 自分の全ての合法手を試す
    for my_x, my_y in valid_moves:
        # 自分の手を打った後の盤面を作成
        test_board = copy(board)
        move_stone(test_board, stone, my_x, my_y)

        # 相手の応手を全て試す
        opponent_moves = get_valid_moves(test_board, opponent)

        if not opponent_moves:
            # 相手が打てない場合、この盤面を評価
            score = evaluate_board(test_board, stone)
        else:
            # 相手が最善手を打つと仮定（ミニマックス）
            worst_score = float('inf')

            for opp_x, opp_y in opponent_moves:
                # 相手の手を打った後の盤面を作成
                test_board2 = copy(test_board)
                move_stone(test_board2, opponent, opp_x, opp_y)

                # その盤面を評価
                score = evaluate_board(test_board2, stone)

                # 相手にとって最善（自分にとって最悪）のスコアを記録
                if score < worst_score:
                    worst_score = score

            score = worst_score

        # 最も有利な手を選択
        if score > best_score:
            best_score = score
            best_move = (my_x, my_y)
      
    
    # time.sleep(0.5)
    return best_move

