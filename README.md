# othello2025
2025年度発展プログラミングでのオセロ対戦システムです。
sakuraを使います

## Google Colabでの使い方

### 1. リポジトリをクローン
```python
# クローン先のフォルダ名は任意（例：hachi, myai, othello等）
!git clone https://github.com/YuuhaNi/othello2025.git hachi
```

### 2. 自分のAI関数を定義、またはインポート
```python
# 例1: 自分でAI関数を定義
def my_ai(board, stone):
    # あなたのオセロAIのロジック
    # ...
    return (x, y)  # 打つ手の座標を返す

# 例2: othello_myai.pyからインポート
from hachi.othello.othello_myai import myai
```

### 3. AI対戦を実行（7行で結果表示）
```python
from hachi.tournament import battle_with_myai

# 自分で定義した関数を渡す
battle_with_myai(my_ai)

# または、インポートした関数を渡す
battle_with_myai(myai)
```

### 出力例
```
========================================
1. vs 🤑 (先攻): 勝 - 18枚
2. vs 🤑 (後攻): 負 - 15枚
3. vs 📐 (先攻): 勝 - 20枚
4. vs 📐 (後攻): 負 - 14枚
5. vs 🔮 (先攻): 負 - 12枚
6. vs 🔮 (後攻): 負 - 11枚
総獲得枚数: 90枚
========================================
```

### 対戦相手のAI（6x6盤面）
- 🤑 GreedyAI: 毎回最も多く石をひっくり返せる手を選ぶ貪欲AI
- 📐 CornerAI: 角を最優先で取るAI
- 🔮 LookaheadAI: 2手先を読んで最善手を選ぶAI