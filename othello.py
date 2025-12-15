import os
try:
    from kogi_canvas import Canvas
except ImportError:
    os.system('pip install kogi_canvas')
    from kogi_canvas import Canvas

import math
import random
import time

BLACK=1
WHITE=2

board = [
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,1,2,0,0],
        [0,0,2,1,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
]

def can_place_x_y(board, stone, x, y):
    """
    石を置けるかどうかを調べる関数。
    board: 2次元配列のオセロボード
    x, y: 石を置きたい座標 (0-indexed)
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    return: 置けるなら True, 置けないなら False
    """
    if board[y][x] != 0:
        return False  # 既に石がある場合は置けない

    opponent = 3 - stone  # 相手の石 (1なら2、2なら1)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True  # 石を置ける条件を満たす

    return False

def can_place(board, stone):
    """
    石を置ける場所を調べる関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                return True
    return False

def random_place(board, stone):
    """
    石をランダムに置く関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    while True:
        x = random.randint(0, len(board[0]) - 1)
        y = random.randint(0, len(board) - 1)
        if can_place_x_y(board, stone, x, y):
            return x, y

def copy(board):
    """
    盤面をコピーする関数。
    board: 2次元配列のオセロボード
    """
    return [row[:] for row in board]


def move_stone(board, stone, x, y):
    """
    石を置き、ひっくり返す関数。
    board: 2次元配列のオセロボード
    x, y: 石を置きたい座標 (0-indexed)
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    return:
    """
    moves = [copy(board)]*3
    if not can_place_x_y(board, stone, x, y):
        return moves  # 置けない場合は何もしない

    board[y][x] = stone  # 石を置く
    moves.append(copy(board))
    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    flipped_count = 0

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy

        if stones_to_flip and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            for flip_x, flip_y in stones_to_flip:
                board[flip_y][flip_x] = stone
                moves.append(copy(board))
                flipped_count += 1

    return moves


class PandaAI(object):

    def __init__(self, func=None):  
        if func is None:
            self.othello_function = random_place
        else:
            self.othello_function = func

    def face(self):
        return "🐼"

    def place(self, board, stone):
        x, y = self.othello_function(board, stone)
        return x, y

def safe_face(panda):
    if hasattr(panda, 'face'):
        return panda.face()
    if callable(panda):
        return "😺"
    return "🐶"

def safe_place(panda, board, stone):
    if hasattr(panda, 'place'):
        return panda.place(board, stone)
    if callable(panda):
        return panda(board, stone)
    return random_place(board, stone)

def draw_board(canvas, board):
    ctx = canvas.getContext("2d")
    grid = width // len(board)
    for y, line in enumerate(board):
        for x, stone in enumerate(line):
            cx = x * grid + grid // 2
            cy = y * grid + grid // 2
            if stone != 0:
                ctx.beginPath()
                ctx.arc(cx, cy, grid//2, 0, 2 * math.pi) # 円の描画
                ctx.fillStyle = "black" if stone == 1 else "white"
                ctx.fill()

width=300

def draw_board_moves(canvas, moves):
    for board in moves:
        draw_board(canvas, board)

def play_othello(ai=None, board=None):
    if board == 8:
        board = [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,1,2,0,0,0],
            [0,0,0,2,1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ]
    elif board is None or board==6:
        board = [
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,1,2,0,0],
            [0,0,2,1,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
        ]
    if ai is None:
        ai = PandaAI()

    def redraw(canvas, x, y):
        nonlocal board, ai
        N = len(board)
        grid = width // N
        x = x // grid
        y = y // grid
        if not can_place_x_y(board, BLACK, x, y):
            print('そこに置けません', (x, y))
            return

        moves = []
        moves.extend(move_stone(board, BLACK, x, y))

        if can_place(board, WHITE):
            x, y = safe_place(ai, board, WHITE)
            if not can_place_x_y(board, WHITE, x, y):
                print(f'{safe_face(ai)}は、置けないところに置こうとしました', (x, y))
                print('反則負けです')
                return
            print(f'{safe_face(ai)}は', (x, y), 'におきました。')
            moves.extend(move_stone(board, WHITE, x, y))
        else:
            print(f'{safe_face(ai)}はどこにも置けないのでスキップします')

        while not can_place(board, BLACK):
            if can_place(board, WHITE):
                print(f'あなたはどこにも置けないのでスキップします')
                x, y = safe_place(ai,board, WHITE)
                print(f'{safe_face(ai)}は', (x, y), 'におきました。')
                moves.extend(move_stone(board, WHITE, x, y))
            else:
                black = sum(row.count(BLACK) for row in board)
                white = sum(row.count(WHITE) for row in board)
                print(f'黒: {black}, 白: {white}', end=' ')
                if black > white:
                    print('黒の勝ち')
                elif black < white:
                    print('白の勝ち')
                else:
                    print('引き分け')
                break
        draw_board_moves(canvas, moves)

    canvas = Canvas(background='green', grid=width//len(board), width=width, height=width, onclick=redraw)
    draw_board(canvas, board)

    display(canvas)

play = play_othello

def count_stone(board):
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white

def run_othello(blackai=None, whiteai=None, board=None, width=300):
    if board == 8:
        board = [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,1,2,0,0,0],
            [0,0,0,2,1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ]
    elif board is None or board==6:
        board = [
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,1,2,0,0],
            [0,0,2,1,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
        ]

    if blackai is None:
        blackai = PandaAI()

    if whiteai is None:
        whiteai = PandaAI()
        print(f'{safe_face(whiteai)}が相手するよ！覚悟しな！')
    print(f'先手 黒 {safe_face(blackai)} 後手 白 {safe_face(whiteai)}')
    board = copy(board)
    black_time = 0
    white_time = 0
    moved = True
    while moved or can_place(board, BLACK) or can_place(board, WHITE):
        moved = False
        if can_place(board, BLACK):
            start = time.time()
            x, y = safe_place(blackai, copy(board), BLACK)
            black_time += time.time() - start
            if not can_place_x_y(board, BLACK, x, y):
                print(f'黒 {safe_face(blackai)}は、置けないところに置こうとしました', (x, y))
                print('反則負けです')
                return
            move_stone(board, BLACK, x, y)
            black, white = count_stone(board)
            print(f'黒 {safe_face(blackai)}は{(x, y)}におきました。黒: {black}, 白: {white}')
            moved = True
        else:
            print(f'{safe_face(blackai)}は、どこにも置けないのでスキップします')

        if can_place(board, WHITE):
            start = time.time()
            x, y = safe_place(whiteai,copy(board), WHITE)
            white_time += time.time() - start
            if not can_place_x_y(board, WHITE, x, y):
                print(f'白 {safe_face(whiteai)}は、置けないところに置こうとしました', (x, y))
                print('反則負けです')
                return
            move_stone(board, WHITE, x, y)
            black, white = count_stone(board)
            print(f'白 {safe_face(whiteai)}は{(x, y)}におきました。黒: {black}, 白: {white}')
            moved = True
        else:
            print(f'{safe_face(whiteai)}は、どこにも置けないのでスキップします')
        
    black, white = count_stone(board)
    print(f'最終結果: 黒 {safe_face(blackai)}: {black}, 白 {safe_face(whiteai)}: {white}', end=' ')
    if black > white:
        print(f'黒 {safe_face(blackai)}の勝ち')
    elif black < white:
        print(f'白 {safe_face(whiteai)}の勝ち')
    else:
        print('引き分け')
    
    canvas = Canvas(background='green', grid=width//len(board), width=width, height=width)
    draw_board(canvas, board)
    display(canvas)
    print(f'思考時間: 黒 {safe_face(blackai)}: {black_time:.5f}秒, 白 {safe_face(whiteai)}: {white_time:.5f}秒')
    return black, white

run = run_othello
