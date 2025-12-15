"""
オセロAIトーナメントシステム
ユーザーが作成したAIと既存のAIを対戦させ、勝ち点を計算する
"""

import json
import sys
import traceback
import argparse
import os

sys.path.append('ai')

from othello import can_place_x_y, copy, move_stone, can_place, safe_place, BLACK, WHITE
from greedy_ai import GreedyAI
from corner_ai import CornerAI
from lookahead_ai import LookaheadAI


class UserAIAdapter:
    """ユーザーのAIコードを既存のインターフェースに適合させるアダプター"""

    def __init__(self, code, user_id):
        self.code = code
        self.user_id = user_id
        self.ai_function = None
        self.ai_instance = None
        self.error = None

        # コードを実行して関数/クラスを抽出
        self._load_ai()

    def _load_ai(self):
        """ユーザーのコードを実行してAI関数/クラスを取得"""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("AI loading timeout - possible infinite loop or input() call")

        try:
            # 安全な実行環境を作成
            # 標準入力をブロックする関数（SystemExitで強制停止）
            def blocked_input(*args):
                raise SystemExit("input() is not allowed in tournament mode")

            # __builtins__をコピーしてinputを置き換え
            import builtins
            import sys
            safe_builtins = {name: getattr(builtins, name) for name in dir(builtins)}
            safe_builtins['input'] = blocked_input

            # tkinterなどのGUIモジュールをブロック
            class BlockedModule:
                def __getattr__(self, name):
                    raise ImportError(f"Module is blocked in tournament mode")

            # sys.modulesを一時的に保存
            original_modules = sys.modules.copy()
            sys.modules['tkinter'] = BlockedModule()
            sys.modules['turtle'] = BlockedModule()
            sys.modules['pygame'] = BlockedModule()

            exec_vars = {
                '__builtins__': safe_builtins,
                'can_place_x_y': can_place_x_y,
                'copy': copy,
                'move_stone': move_stone,
                'List': list,  # 型ヒント用
                'Tuple': tuple,
                'Optional': type(None),
                'time': __import__('time'),
                'defaultdict': __import__('collections').defaultdict,
            }

            # コードを実行（local_varsを省略して全てexec_varsに入れる）
            # これにより関数間の参照が正しく動作する
            # __name__を設定してif __name__ == "__main__"ブロックを実行させない
            exec_vars['__name__'] = '__tournament__'

            # タイムアウトを設定（1秒）
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1)
            try:
                exec(self.code, exec_vars)
            except (SystemExit, KeyboardInterrupt):
                # input()やmainloop()などでブロックされた場合
                raise TimeoutError("Code execution blocked (input/GUI detected)")
            finally:
                signal.alarm(0)  # タイムアウト解除

            # 関数またはクラスを探す
            # よくある関数名: myai, othello_ai, ai_move, get_best_move
            function_names = ['myai', 'othello_ai', 'ai_move', 'get_best_move',
                            'greedy_place', 'corner_place', 'lookahead_place']

            for name in function_names:
                if name in exec_vars and callable(exec_vars[name]):
                    self.ai_function = exec_vars[name]
                    break

            # クラスを探す
            class_names = ['OthelloAI', 'AI', 'MyAI']
            for name in class_names:
                if name in exec_vars and isinstance(exec_vars[name], type):
                    try:
                        self.ai_instance = exec_vars[name]()
                    except:
                        pass
                    break

            if not self.ai_function and not self.ai_instance:
                self.error = "AI関数またはクラスが見つかりません"

            # sys.modulesを復元
            sys.modules.update(original_modules)
            for key in list(sys.modules.keys()):
                if key not in original_modules:
                    del sys.modules[key]

        except Exception as e:
            # sys.modulesを復元
            import sys
            if 'original_modules' in locals():
                sys.modules.update(original_modules)
                for key in list(sys.modules.keys()):
                    if key not in original_modules:
                        del sys.modules[key]
            self.error = f"コード実行エラー: {str(e)}\n{traceback.format_exc()}"

    def face(self):
        return f"👤"  # ユーザーAI

    def place(self, board, stone):
        """既存のインターフェースに適合した手を返す"""
        try:
            # ボードを6x6または8x8に変換（ユーザーコードに応じて）
            size = len(board)

            # クラスインスタンスの場合
            if self.ai_instance:
                # get_best_move, get_ai_move, place などのメソッドを探す
                if hasattr(self.ai_instance, 'get_best_move'):
                    result = self.ai_instance.get_best_move(board, stone)
                elif hasattr(self.ai_instance, 'get_ai_move'):
                    # OthelloAIクラスのようなもの
                    self.ai_instance.board = board
                    result = self.ai_instance.get_ai_move()
                elif hasattr(self.ai_instance, 'place'):
                    result = self.ai_instance.place(board, stone)
                else:
                    return None

            # 関数の場合
            elif self.ai_function:
                # 関数のシグネチャに応じて呼び出す
                import inspect
                sig = inspect.signature(self.ai_function)
                params = list(sig.parameters.keys())

                if len(params) == 2:
                    # myai(board, color) のような形式
                    result = self.ai_function(board, stone)
                elif len(params) == 1:
                    # othello_ai(board) のような形式（プレイヤー固定）
                    result = self.ai_function(board)
                else:
                    return None
            else:
                return None

            # 結果の形式を統一: (x, y) または (row, col)
            if result and isinstance(result, tuple) and len(result) == 2:
                # (col, row) または (row, col) の可能性がある
                # 盤面の範囲チェックで判断
                x, y = result
                if 0 <= x < size and 0 <= y < size:
                    return result
                # 逆かもしれない
                elif 0 <= y < size and 0 <= x < size:
                    return (y, x)

            return None

        except Exception as e:
            print(f"Error in user AI ({self.user_id}): {e}")
            return None


def load_user_ais(jsonl_path):
    """JSONLファイルからユーザーAIを読み込む"""
    user_ais = []

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                user_id = data.get('userId')
                generation_id = data.get('generationId')
                code = data.get('code')

                if generation_id and code:
                    adapter = UserAIAdapter(code, generation_id)
                    if adapter.error:
                        print(f"Error loading AI for {generation_id} (user: {user_id}): {adapter.error}")
                        # エラーでもリストに追加（score 0として記録するため）
                        user_ais.append((generation_id, adapter, data))
                    else:
                        user_ais.append((generation_id, adapter, data))

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                continue

    return user_ais


def count_stones(board, stone):
    """盤面上の指定した色の石の数を数える"""
    return sum(row.count(stone) for row in board)


def run_match(ai1, ai2, board_size=6, max_turns=100):
    """
    2つのAIを対戦させる（displayなしの独自実装）

    Returns:
        (result, black_count, white_count)
        result: 1=黒の勝ち, 2=白の勝ち, 0=引き分け, -1=エラー
        black_count: 黒の最終石数
        white_count: 白の最終石数
    """
    try:
        # 初期盤面
        if board_size == 8:
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
        else:  # 6x6
            board = [
                [0,0,0,0,0,0],
                [0,0,0,0,0,0],
                [0,0,1,2,0,0],
                [0,0,2,1,0,0],
                [0,0,0,0,0,0],
                [0,0,0,0,0,0],
            ]

        moved = True
        turn_count = 0

        while moved and turn_count < max_turns:
            moved = False
            turn_count += 1

            # 黒(ai1)のターン
            if can_place(board, BLACK):
                try:
                    x, y = safe_place(ai1, copy(board), BLACK)
                    if x is not None and y is not None and can_place_x_y(board, BLACK, x, y):
                        move_stone(board, BLACK, x, y)
                        moved = True
                    else:
                        # 無効な手 = 反則負け
                        black_count = count_stones(board, BLACK)
                        white_count = count_stones(board, WHITE)
                        return (2, black_count, white_count)  # 白の勝ち
                except Exception as e:
                    # エラー（盤面サイズ非対応など）= AI動作不能
                    print(f"  AI1 error: {e}")
                    return (-1, 0, 0)

            # 白(ai2)のターン
            if can_place(board, WHITE):
                try:
                    x, y = safe_place(ai2, copy(board), WHITE)
                    if x is not None and y is not None and can_place_x_y(board, WHITE, x, y):
                        move_stone(board, WHITE, x, y)
                        moved = True
                    else:
                        # 無効な手 = 反則負け
                        black_count = count_stones(board, BLACK)
                        white_count = count_stones(board, WHITE)
                        return (1, black_count, white_count)  # 黒の勝ち
                except Exception as e:
                    # エラー（盤面サイズ非対応など）= AI動作不能
                    print(f"  AI2 error: {e}")
                    return (-1, 0, 0)

            # 両者とも打てない場合は終了
            if not can_place(board, BLACK) and not can_place(board, WHITE):
                break

        # 石の数を数えて勝敗を判定
        black_count = count_stones(board, BLACK)
        white_count = count_stones(board, WHITE)

        if black_count > white_count:
            return (1, black_count, white_count)  # 黒の勝ち
        elif black_count < white_count:
            return (2, black_count, white_count)  # 白の勝ち
        else:
            return (0, black_count, white_count)  # 引き分け

    except Exception as e:
        print(f"Match error: {e}")
        traceback.print_exc()
        return (-1, 0, 0)  # エラー


def calculate_scores(user_ais, reference_ais, board_size=6):
    """
    各ユーザーAIと基準AIを対戦させ、スコアを計算

    スコアリング:
    - 勝ち: 3点
    - 引き分け: 2点
    - 負け: 1点
    - エラー/動かない: 0点

    Args:
        user_ais: [(generation_id, adapter, original_data), ...]
        reference_ais: [AI1, AI2, AI3, ...]
        board_size: 盤面サイズ

    Returns:
        {generation_id: (score, original_data), ...}
    """
    results = {}

    for generation_id, user_ai, original_data in user_ais:
        total_score = 0
        matches_played = 0

        user_id = original_data.get('userId', 'unknown')
        print(f"\n=== {generation_id} (user: {user_id}) ===")

        # エラーで読み込めなかったAIは0点
        if user_ai.error:
            print(f"  AI読み込みエラーのため対戦スキップ: {user_ai.error[:50]}...")
            data_with_stones = original_data.copy()
            data_with_stones['stonesCount_total'] = 0
            # 全ての対戦相手のフィールドを0で埋める
            for ref_ai in reference_ais:
                opponent_name = ref_ai.__class__.__name__
                data_with_stones[f'stonesCount_{opponent_name}_senkou'] = 0
                data_with_stones[f'stonesCount_{opponent_name}_koukou'] = 0
            results[generation_id] = (0, data_with_stones)
            continue

        # 実行時エラーチェック用フラグ
        is_ai_working = True
        total_stones_taken = 0  # ユーザーAIが取った石の合計
        stones_by_opponent = {}  # 対戦相手ごとの石の数

        for ref_ai in reference_ais:
            opponent_name = ref_ai.__class__.__name__  # 'GreedyAI', 'CornerAI', 'LookaheadAI'
            opponent_stones_black = 0  # 先攻（黒番）
            opponent_stones_white = 0  # 後攻（白番）

            # ユーザーAI(黒) vs 基準AI(白)
            result1, black_count, white_count = run_match(user_ai, ref_ai, board_size)
            if result1 == 1:
                total_score += 3  # 勝ち
                total_stones_taken += black_count
                opponent_stones_black = black_count
                print(f"  vs {ref_ai.face()}: WIN (黒) +3 [{black_count}-{white_count}]")
            elif result1 == 0:
                total_score += 2  # 引き分け
                total_stones_taken += black_count
                opponent_stones_black = black_count
                print(f"  vs {ref_ai.face()}: DRAW (黒) +2 [{black_count}-{white_count}]")
            elif result1 == 2:
                total_score += 1  # 負け
                total_stones_taken += black_count
                opponent_stones_black = black_count
                print(f"  vs {ref_ai.face()}: LOSE (黒) +1 [{black_count}-{white_count}]")
            else:
                # エラー：盤面サイズ非対応など実行不能
                print(f"  vs {ref_ai.face()}: ERROR (黒) - AI動作不能のため0点扱い")
                is_ai_working = False
                break

            matches_played += 1

            # 基準AI(黒) vs ユーザーAI(白)
            result2, black_count, white_count = run_match(ref_ai, user_ai, board_size)
            if result2 == 2:
                total_score += 3  # 勝ち
                total_stones_taken += white_count
                opponent_stones_white = white_count
                print(f"  vs {ref_ai.face()}: WIN (白) +3 [{black_count}-{white_count}]")
            elif result2 == 0:
                total_score += 2  # 引き分け
                total_stones_taken += white_count
                opponent_stones_white = white_count
                print(f"  vs {ref_ai.face()}: DRAW (白) +2 [{black_count}-{white_count}]")
            elif result2 == 1:
                total_score += 1  # 負け
                total_stones_taken += white_count
                opponent_stones_white = white_count
                print(f"  vs {ref_ai.face()}: LOSE (白) +1 [{black_count}-{white_count}]")
            else:
                # エラー：盤面サイズ非対応など実行不能
                print(f"  vs {ref_ai.face()}: ERROR (白) - AI動作不能のため0点扱い")
                is_ai_working = False
                break

            matches_played += 1
            stones_by_opponent[opponent_name] = {
                'black': opponent_stones_black,
                'white': opponent_stones_white
            }

        # エラーが出たAIは0点
        if not is_ai_working:
            data_with_stones = original_data.copy()
            data_with_stones['stonesCount_total'] = 0
            # 全ての対戦相手のフィールドを0で埋める
            for ref_ai in reference_ais:
                opponent_name = ref_ai.__class__.__name__
                data_with_stones[f'stonesCount_{opponent_name}_senkou'] = 0
                data_with_stones[f'stonesCount_{opponent_name}_koukou'] = 0
            results[generation_id] = (0, data_with_stones)
            print(f"  Total Score: 0 (AI動作不能)")
            continue

        # フラットな構造に変換（トップレベルに追加）
        data_with_stones = original_data.copy()
        data_with_stones['stonesCount_total'] = total_stones_taken
        for opponent, counts in stones_by_opponent.items():
            data_with_stones[f'stonesCount_{opponent}_senkou'] = counts['black']
            data_with_stones[f'stonesCount_{opponent}_koukou'] = counts['white']

        results[generation_id] = (total_score, data_with_stones)
        print(f"  Total Score: {total_score} ({matches_played} matches, {total_stones_taken} stones)")
        for opponent, counts in stones_by_opponent.items():
            print(f"    {opponent}: 黒{counts['black']} + 白{counts['white']} = {counts['black'] + counts['white']}")

    return results


def save_results(results, output_path):
    """結果をJSONL形式で保存（元のデータ + score）"""
    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        for generation_id, (score, original_data) in results.items():
            # 元のデータをコピーしてscoreを追加
            result = original_data.copy()
            result['score'] = score
            f.write(json.dumps(result, ensure_ascii=False) + '\n')


def main():
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(description='オセロAIトーナメントシステム')
    parser.add_argument('input_file',
                        nargs='?',
                        default='userdata/filtered_logs_after20251201_test.jsonl',
                        help='ユーザーAIが含まれるJSONLファイルのパス（デフォルト: userdata/filtered_logs_after20251201_test.jsonl）')
    parser.add_argument('-o', '--output',
                        default='results/tournament_results.jsonl',
                        help='結果を保存するJSONLファイルのパス（デフォルト: results/tournament_results.jsonl）')
    parser.add_argument('-s', '--size',
                        type=int,
                        choices=[6, 8],
                        default=6,
                        help='盤面サイズ（6または8、デフォルト: 6）')

    args = parser.parse_args()

    # JSONLファイルからユーザーAIを読み込む
    print(f"Loading user AIs from: {args.input_file}")
    user_ais = load_user_ais(args.input_file)
    print(f"Loaded {len(user_ais)} user AIs")

    # 基準AI（対戦相手）- aiフォルダ内のAI
    reference_ais = [
        GreedyAI(),      # 貪欲AI 🤑
        CornerAI(),      # 角優先AI 📐
        LookaheadAI(),   # 先読みAI 🔮
    ]

    # トーナメント実行
    print(f"\n=== Starting Tournament (Board Size: {args.size}x{args.size}) ===")
    results = calculate_scores(user_ais, reference_ais, board_size=args.size)

    # 結果を保存
    save_results(results, args.output)
    print(f"\n=== Results saved to {args.output} ===")

    # 結果を表示
    print("\n=== Final Rankings ===")
    sorted_results = sorted(results.items(), key=lambda x: x[1][0], reverse=True)
    for rank, (generation_id, (score, data)) in enumerate(sorted_results, 1):
        user_id = data.get('userId', 'unknown')
        print(f"{rank}. {generation_id} (user: {user_id}): {score} points")


def battle_with_myai(myai_func, board_size=6):
    """
    Google Colab用：myai関数とaiフォルダ内のAIを対戦させ、7行で結果を出力

    使い方 (Google Colabで):
        !git clone https://github.com/YuuhaNi/othello2025.git hachi
        from hachi import myai
        from hachi.tournament import battle_with_myai
        battle_with_myai(myai)

    Args:
        myai_func: myai関数 (board, stone) -> (x, y)
        board_size: 盤面サイズ (6 or 8)
    """
    # myai関数をPandaAIラッパーにする
    class MyAIWrapper:
        def __init__(self, func):
            self.func = func

        def face(self):
            return "🎓"

        def place(self, board, stone):
            return self.func(board, stone)

    myai_wrapper = MyAIWrapper(myai_func)

    # 基準AI
    reference_ais = [
        GreedyAI(),      # 貪欲AI 🤑
        CornerAI(),      # 角優先AI 📐
        LookaheadAI(),   # 先読みAI 🔮
    ]

    # 対戦結果を記録
    results = []
    total_stones = 0

    # 各AIと2回ずつ対戦（先攻・後攻）
    for ref_ai in reference_ais:
        # 先攻（黒番）
        result1, black_count, white_count = run_match(myai_wrapper, ref_ai, board_size)
        results.append({
            'opponent': ref_ai.face(),
            'turn': '先攻',
            'result': result1,
            'stones': black_count
        })
        if result1 != -1:
            total_stones += black_count

        # 後攻（白番）
        result2, black_count, white_count = run_match(ref_ai, myai_wrapper, board_size)
        results.append({
            'opponent': ref_ai.face(),
            'turn': '後攻',
            'result': result2,
            'stones': white_count
        })
        if result2 != -1:
            total_stones += white_count

    # 7行で結果を出力
    print("=" * 40)
    for i, r in enumerate(results, 1):
        result_str = "勝" if (r['turn'] == '先攻' and r['result'] == 1) or (r['turn'] == '後攻' and r['result'] == 2) else \
                     "負" if (r['turn'] == '先攻' and r['result'] == 2) or (r['turn'] == '後攻' and r['result'] == 1) else \
                     "分" if r['result'] == 0 else "エラー"
        if r['result'] != -1:
            print(f"{i}. vs {r['opponent']} ({r['turn']}): {result_str} - {r['stones']}枚")
        else:
            print(f"{i}. vs {r['opponent']} ({r['turn']}): {result_str}")
    print(f"総獲得枚数: {total_stones}枚")
    print("=" * 40)


if __name__ == "__main__":
    main()
