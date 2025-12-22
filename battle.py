"""
オセロAI対戦システム - リアルタイム盤面表示版
AI同士を対戦させ、リアルタイムで盤面の変化を見ることができます
"""

import time
import sys
import os

# このファイルのディレクトリを自動的にsys.pathに追加
# これにより、ユーザーが手動で%cdやsys.path.appendをしなくても
# othello.pyやai/などをインポートできる
_battle_dir = os.path.dirname(os.path.abspath(__file__))
if _battle_dir not in sys.path:
    sys.path.insert(0, _battle_dir)

try:
    from tqdm import tqdm
except ImportError:
    print("tqdmをインストールしています...")
    import os
    os.system('pip install tqdm')
    from tqdm import tqdm

try:
    # パッケージとして使われる場合
    from .othello import can_place_x_y, copy, move_stone, can_place, safe_place, safe_face, BLACK, WHITE, draw_board
    from kogi_canvas import Canvas
except ImportError:
    # 直接実行される場合
    from othello import can_place_x_y, copy, move_stone, can_place, safe_place, safe_face, BLACK, WHITE, draw_board
    try:
        from kogi_canvas import Canvas
    except ImportError:
        import os
        os.system('pip install kogi_canvas')
        from kogi_canvas import Canvas


def count_stone(board):
    """盤面の石の数を数える"""
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white


def run_othello_live(blackai=None, whiteai=None, board=None, width=300, delay=0.5, name1=None, name2=None):
    """
    AI同士を対戦させ、リアルタイムで盤面を表示する

    Args:
        blackai: 黒のAI (関数またはPandaAI互換オブジェクト)
        whiteai: 白のAI (関数またはPandaAI互換オブジェクト)
        board: 盤面サイズ (6, 8) または盤面の2次元配列
        width: Canvasの幅（デフォルト: 300）
        delay: 各手の後の待機時間（秒）

    Returns:
        (black_count, white_count, winner): 最終結果
            winner: 'black', 'white', 'draw', 'error'
    """
    # 盤面の初期化
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
    elif board is None or board == 6:
        board = [
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,1,2,0,0],
            [0,0,2,1,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
        ]
    else:
        board = copy(board)

    # AIがNoneの場合はランダムAIを使用
    from othello import PandaAI
    if blackai is None:
        blackai = PandaAI()
    if whiteai is None:
        whiteai = PandaAI()

    # 内部処理用にアイコンを取得（ログ出力用）
    black_icon = safe_face(blackai)
    white_icon = safe_face(whiteai)

    # 名前が指定されていない場合はアイコンを使用
    if name1 is None:
        name1 = black_icon
    if name2 is None:
        name2 = white_icon

    print(f'先攻（黒）: {name1}')
    print(f'後攻（白）: {name2}')

    board = copy(board)
    black_time = 0
    white_time = 0
    turn_count = 0
    max_turns = len(board) * len(board[0]) * 2  # 最大手数

    black_error = False
    white_error = False

    # IPython.displayをインポート
    try:
        from IPython.display import clear_output
        has_ipython = True
    except ImportError:
        has_ipython = False

    # Canvasを作成して初期表示
    print(f'先攻（黒）: {name1}  vs  後攻（白）: {name2}')
    canvas = Canvas(background='green', grid=width//len(board), width=width, height=width)
    draw_board(canvas, board)
    display(canvas)

    # tqdmで進捗を表示
    with tqdm(total=max_turns, desc="対戦進行中", ncols=80) as pbar:
        moved = True
        while moved or can_place(board, BLACK) or can_place(board, WHITE):
            moved = False

            # 黒のターン
            if can_place(board, BLACK):
                try:
                    start = time.time()
                    x, y = safe_place(blackai, copy(board), BLACK)
                    think_time = time.time() - start
                    black_time += think_time

                    if not can_place_x_y(board, BLACK, x, y):
                        print(f'黒 {name1}は、置けないところに置こうとしました {(x, y)}')
                        print('反則負けです')
                        black_error = True
                        break

                    move_stone(board, BLACK, x, y)
                    black, white = count_stone(board)
                    print(f'黒 {name1}は{(x, y)}におきました。黒: {black}, 白: {white} (思考時間: {think_time:.5f}秒)')

                    turn_count += 1
                    pbar.update(1)

                    # 盤面を更新（その場で更新）
                    time.sleep(delay)
                    if has_ipython:
                        clear_output(wait=True)
                    print(f'先攻（黒）: {name1}  vs  後攻（白）: {name2}')
                    canvas = Canvas(background='green', grid=width//len(board), width=width, height=width)
                    draw_board(canvas, board)
                    display(canvas)

                    moved = True
                except Exception as e:
                    print(f'黒 {name1}でエラーが発生しました: {e}')
                    print('エラーのため黒の石は0個として扱います')
                    black_error = True
                    break
            else:
                if can_place(board, WHITE):
                    print(f'{name1}は、どこにも置けないのでスキップします')

            # 白のターン
            if can_place(board, WHITE):
                try:
                    start = time.time()
                    x, y = safe_place(whiteai, copy(board), WHITE)
                    think_time = time.time() - start
                    white_time += think_time

                    if not can_place_x_y(board, WHITE, x, y):
                        print(f'白 {name2}は、置けないところに置こうとしました {(x, y)}')
                        print('反則負けです')
                        white_error = True
                        break

                    move_stone(board, WHITE, x, y)
                    black, white = count_stone(board)
                    print(f'白 {name2}は{(x, y)}におきました。黒: {black}, 白: {white} (思考時間: {think_time:.5f}秒)')

                    turn_count += 1
                    pbar.update(1)

                    # 盤面を更新（その場で更新）
                    time.sleep(delay)
                    if has_ipython:
                        clear_output(wait=True)
                    print(f'先攻（黒）: {name1}  vs  後攻（白）: {name2}')
                    canvas = Canvas(background='green', grid=width//len(board), width=width, height=width)
                    draw_board(canvas, board)
                    display(canvas)

                    moved = True
                except Exception as e:
                    print(f'白 {name2}でエラーが発生しました: {e}')
                    print('エラーのため白の石は0個として扱います')
                    white_error = True
                    break
            else:
                if can_place(board, BLACK):
                    print(f'{name2}は、どこにも置けないのでスキップします')

            # 両方とも打てない場合は終了
            if not can_place(board, BLACK) and not can_place(board, WHITE):
                break

    # エラー処理
    if black_error:
        black, white = 0, count_stone(board)[1]
    elif white_error:
        black, white = count_stone(board)[0], 0
    else:
        black, white = count_stone(board)

    print(f'最終結果: 黒 {name1}: {black}, 白 {name2}: {white}', end=' ')

    # 勝者の判定
    if black > white:
        winner = 'black'
        print(f'黒 {name1}の勝ち')
    elif black < white:
        winner = 'white'
        print(f'白 {name2}の勝ち')
    else:
        winner = 'draw'
        print('引き分け')

    print(f'思考時間: 黒 {name1}: {black_time:.5f}秒, 白 {name2}: {white_time:.5f}秒')

    return black, white, winner


def _battle_single(myai1, myai2, name1="AI1", name2="AI2", board_size=6, width=300, delay=0.5):
    """
    内部関数: 2つのmyai関数を1試合だけ対戦させる
    """
    from othello import PandaAI

    # 名前を設定するためにカスタムクラスを作成
    class NamedAI:
        def __init__(self, func, name):
            self.func = func
            self.name_str = name

        def face(self):
            return f"🎓"

        def name(self):
            return self.name_str

        def place(self, board, stone):
            return self.func(board, stone)

    ai1_named = NamedAI(myai1, name1)
    ai2_named = NamedAI(myai2, name2)

    # 対戦実行（名前を渡す）
    black, white, winner = run_othello_live(ai1_named, ai2_named, board_size, width, delay, name1, name2)

    print(f"\n{'='*60}")
    print(f"  対戦結果")
    print(f"{'='*60}")
    print(f"  {name1} (黒): {black}個")
    print(f"  {name2} (白): {white}個")
    if winner == 'black':
        print(f"  🏆 勝者: {name1}")
    elif winner == 'white':
        print(f"  🏆 勝者: {name2}")
    else:
        print(f"  🤝 引き分け")
    print(f"{'='*60}\n")

    return black, white, winner


def battle_myais(myai1, myai2, name1="AI1", name2="AI2", board_size=6, width=300, delay=0.5):
    """
    2つのmyai関数を先攻・後攻を入れ替えて2試合対戦させる

    使い方:
        # GitHubからクローン
        !git clone https://github.com/user1/othello2025.git a008
        !git clone https://github.com/user2/othello2025.git a009

        # Pythonパスに追加 (Colabの場合)
        import sys
        sys.path.append('/content/a008')
        sys.path.append('/content/a009')

        # またはディレクトリ移動
        %cd a008

        # インポート
        from a008 import myai as myai008
        from a009 import myai as myai009

        # 対戦
        from battle import battle_myais
        battle_myais(myai008, myai009, name1="a008", name2="a009", delay=0.5)

    Args:
        myai1: 1つ目のmyai関数
        myai2: 2つ目のmyai関数
        name1: AI1の名前（表示用）
        name2: AI2の名前（表示用）
        board_size: 盤面サイズ (6 or 8)
        width: Canvasの幅
        delay: 各手の待機時間

    Returns:
        results: 2試合の結果
    """
    print(f"\n{'='*60}")
    print(f"  先攻・後攻入れ替え2試合対戦")
    print(f"  {name1} vs {name2}")
    print(f"{'='*60}\n")

    # 第1試合: myai1が先攻（黒）
    print(f"\n【第1試合】 {name1} (黒/先攻) vs {name2} (白/後攻)")
    black1, white1, winner1 = _battle_single(myai1, myai2, name1, name2, board_size, width, delay)

    # 第2試合: myai2が先攻（黒）
    print(f"\n【第2試合】 {name2} (黒/先攻) vs {name1} (白/後攻)")
    black2, white2, winner2 = _battle_single(myai2, myai1, name2, name1, board_size, width, delay)

    # 総合結果
    print(f"\n{'='*60}")
    print(f"  総合結果（2試合）")
    print(f"{'='*60}")

    # 獲得石数の合計
    total1 = black1 + white2  # myai1の合計
    total2 = white1 + black2  # myai2の合計

    # 勝ち数
    wins1 = 0
    wins2 = 0
    draws = 0

    if winner1 == 'black':
        wins1 += 1
    elif winner1 == 'white':
        wins2 += 1
    else:
        draws += 1

    if winner2 == 'black':
        wins2 += 1
    elif winner2 == 'white':
        wins1 += 1
    else:
        draws += 1

    print(f"  {name1}: {wins1}勝 {draws}分 {2-wins1-draws}敗 (合計{total1}個)")
    print(f"  {name2}: {wins2}勝 {draws}分 {2-wins2-draws}敗 (合計{total2}個)")

    if wins1 > wins2:
        print(f"  🏆 総合優勝: {name1}")
    elif wins1 < wins2:
        print(f"  🏆 総合優勝: {name2}")
    elif total1 > total2:
        print(f"  🏆 総合優勝（石数差）: {name1}")
    elif total1 < total2:
        print(f"  🏆 総合優勝（石数差）: {name2}")
    else:
        print(f"  🤝 完全引き分け")
    print(f"{'='*60}\n")

    return {
        'game1': (black1, white1, winner1),
        'game2': (black2, white2, winner2),
        'total': {
            name1: {'wins': wins1, 'stones': total1},
            name2: {'wins': wins2, 'stones': total2}
        }
    }


# 後方互換性のためのエイリアス
battle_myais_double = battle_myais


def load_user_ais_from_github(jsonl_path):
    """
    JSONLファイルからユーザーAIを読み込む
    tournament.pyの機能を利用
    """
    try:
        from tournament import load_user_ais
        return load_user_ais(jsonl_path)
    except ImportError:
        print("エラー: tournament.pyが見つかりません")
        return []


def battle_user_ais(jsonl_path, board_size=6, width=300, delay=0.5):
    """
    GitHubに投稿されたユーザーのmyai同士を対戦させる

    Args:
        jsonl_path: ユーザーAIが含まれるJSONLファイルのパス
        board_size: 盤面サイズ (6 or 8)
        width: Canvasの幅
        delay: 各手の待機時間

    使用例:
        from battle import battle_user_ais
        battle_user_ais('userdata/filtered_logs.jsonl', board_size=6, delay=0.3)
    """
    print(f"ユーザーAIを読み込み中: {jsonl_path}")
    user_ais = load_user_ais_from_github(jsonl_path)

    if not user_ais:
        print("エラー: ユーザーAIが見つかりませんでした")
        return

    print(f"{len(user_ais)}個のユーザーAIを読み込みました\n")

    # 正常に読み込めたAIのみを対戦させる
    valid_ais = []
    for generation_id, adapter, original_data in user_ais:
        if not adapter.error:
            user_id = original_data.get('userId', 'unknown')
            valid_ais.append((f"{generation_id} (user: {user_id})", adapter))
        else:
            print(f"スキップ: {generation_id} - {adapter.error[:50]}...")

    if len(valid_ais) < 2:
        print("エラー: 対戦可能なAIが2つ未満です")
        return

    print(f"\n{len(valid_ais)}個のAIで総当たり戦を開始します")
    print("="*50 + "\n")

    results = {name: {'wins': 0, 'losses': 0, 'draws': 0, 'stones': 0}
               for name, _ in valid_ais}

    total_matches = len(valid_ais) * (len(valid_ais) - 1)
    match_num = 0

    for i, (name1, ai1) in enumerate(valid_ais):
        for j, (name2, ai2) in enumerate(valid_ais):
            if i == j:
                continue

            match_num += 1
            print(f"\n【第{match_num}/{total_matches}試合】 {name1} (黒) vs {name2} (白)")

            try:
                black, white, winner = run_othello_live(ai1, ai2, board_size, width, delay)

                # 結果を記録
                results[name1]['stones'] += black
                results[name2]['stones'] += white

                if winner == 'black':
                    results[name1]['wins'] += 1
                    results[name2]['losses'] += 1
                elif winner == 'white':
                    results[name1]['losses'] += 1
                    results[name2]['wins'] += 1
                else:
                    results[name1]['draws'] += 1
                    results[name2]['draws'] += 1
            except Exception as e:
                print(f"対戦中にエラーが発生: {e}")
                continue

    # 最終結果を表示
    print("\n" + "="*50)
    print("  総当たり戦 最終結果")
    print("="*50 + "\n")

    # 勝ち点でソート (勝ち=3点, 引き分け=1点, 負け=0点)
    sorted_results = sorted(
        results.items(),
        key=lambda x: (x[1]['wins'] * 3 + x[1]['draws'], x[1]['stones']),
        reverse=True
    )

    print(f"{'順位':<4} {'AI名':<50} {'勝':<4} {'分':<4} {'負':<4} {'石数':<6} {'勝ち点':<6}")
    print("-" * 80)

    for rank, (name, data) in enumerate(sorted_results, 1):
        points = data['wins'] * 3 + data['draws']
        print(f"{rank:<4} {name:<50} {data['wins']:<4} {data['draws']:<4} "
              f"{data['losses']:<4} {data['stones']:<6} {points:<6}")

    print("="*80 + "\n")

    return results


def battle_tournament(ai_list, board_size=6, width=300, delay=0.3):
    """
    複数のAIで総当たり戦を行う

    Args:
        ai_list: AIのリスト [(name, ai), ...]
        board_size: 盤面サイズ
        width: Canvasの幅
        delay: 各手の待機時間

    Returns:
        results: {ai_name: {'wins': int, 'losses': int, 'draws': int, 'stones': int}}
    """
    results = {name: {'wins': 0, 'losses': 0, 'draws': 0, 'stones': 0}
               for name, _ in ai_list}

    total_matches = len(ai_list) * (len(ai_list) - 1)

    print(f"\n総当たり戦を開始します ({total_matches}試合)")
    print("="*50 + "\n")

    match_num = 0
    for i, (name1, ai1) in enumerate(ai_list):
        for j, (name2, ai2) in enumerate(ai_list):
            if i == j:
                continue

            match_num += 1
            print(f"\n【第{match_num}試合】 {name1} (黒) vs {name2} (白)")

            black, white, winner = run_othello_live(ai1, ai2, board_size, width, delay)

            # 結果を記録
            results[name1]['stones'] += black
            results[name2]['stones'] += white

            if winner == 'black':
                results[name1]['wins'] += 1
                results[name2]['losses'] += 1
            elif winner == 'white':
                results[name1]['losses'] += 1
                results[name2]['wins'] += 1
            else:
                results[name1]['draws'] += 1
                results[name2]['draws'] += 1

    # 最終結果を表示
    print("\n" + "="*50)
    print("  総当たり戦 最終結果")
    print("="*50 + "\n")

    # 勝ち点でソート (勝ち=3点, 引き分け=1点, 負け=0点)
    sorted_results = sorted(
        results.items(),
        key=lambda x: (x[1]['wins'] * 3 + x[1]['draws'], x[1]['stones']),
        reverse=True
    )

    print(f"{'順位':<4} {'AI名':<20} {'勝':<4} {'分':<4} {'負':<4} {'石数':<6} {'勝ち点':<6}")
    print("-" * 50)

    for rank, (name, data) in enumerate(sorted_results, 1):
        points = data['wins'] * 3 + data['draws']
        print(f"{rank:<4} {name:<20} {data['wins']:<4} {data['draws']:<4} "
              f"{data['losses']:<4} {data['stones']:<6} {points:<6}")

    print("="*50 + "\n")

    return results


# テスト用
if __name__ == "__main__":
    print("battle.py - オセロAI対戦システム")
    print("使い方は BATTLE_GUIDE.md を参照してください")
