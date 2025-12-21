# オセロAI対戦システム - 使い方ガイド

`battle.py` を使って、オセロAI同士を対戦させる方法を説明します。

## 1. GitHubからクローンしたmyai同士の1対1対戦

GitHubから2つのリポジトリをクローンして、それぞれの`myai`関数を対戦させます。

```python
# GitHubからリポジトリをクローン
!git clone https://github.com/user1/othello2025.git a008
!git clone https://github.com/user2/othello2025.git a009

# myai関数をインポート
from a008 import myai as myai008
from a009 import myai as myai009

# 対戦させる
from battle import battle_myais
battle_myais(myai008, myai009, name1="a008", name2="a009", delay=0.5)
```

### パラメータ
- `myai1`: 黒番（先攻）のmyai関数
- `myai2`: 白番（後攻）のmyai関数
- `name1`: AI1の名前（表示用）
- `name2`: AI2の名前（表示用）
- `board_size`: 盤面サイズ（6 or 8、デフォルト: 6）
- `width`: Canvasの幅（デフォルト: 300）
- `delay`: 各手の後の待機時間（秒、デフォルト: 0.5）

### 出力
- リアルタイムで盤面が更新される（Canvas表示）
- 各手ごとに座標、石数、思考時間を表示
- 最終結果（勝者、石数、思考時間）を表示

---

## 2. myai同士の先攻・後攻入れ替え2試合対戦

先攻・後攻を入れ替えて2試合行い、総合結果を表示します。

```python
from a008 import myai as myai008
from a009 import myai as myai009

from battle import battle_myais_double
battle_myais_double(myai008, myai009, name1="a008", name2="a009", delay=0.5)
```

### 出力
- 第1試合: myai008 (黒) vs myai009 (白)
- 第2試合: myai009 (黒) vs myai008 (白)
- 総合結果: 勝ち数、石数の合計、総合優勝者

---

## 3. 既存AIとの対戦

aiフォルダ内の既存AI（GreedyAI、CornerAI、LookaheadAI）と対戦させます。

```python
from battle import run_othello_live
from ai.greedy_ai import GreedyAI
from ai.corner_ai import CornerAI

# 貪欲AI vs 角優先AI
run_othello_live(GreedyAI(), CornerAI(), board=6, delay=0.5)
```

### カスタムmyai vs 既存AI

```python
from battle import battle_myais
from ai.greedy_ai import GreedyAI

# myaiをインポート
from a008 import myai as myai008

# カスタムmyai vs 貪欲AI
# 既存AIはplace()メソッドを持つので、そのまま渡せる
from battle import run_othello_live
from othello import PandaAI

run_othello_live(PandaAI(myai008), GreedyAI(), board=6, delay=0.5)
```

---

## 4. 既存AIの総当たり戦

複数の既存AIで総当たり戦を行います。

```python
from battle import battle_tournament
from ai.greedy_ai import GreedyAI
from ai.corner_ai import CornerAI
from ai.lookahead_ai import LookaheadAI

ai_list = [
    ("貪欲AI", GreedyAI()),
    ("角優先AI", CornerAI()),
    ("先読みAI", LookaheadAI()),
]

battle_tournament(ai_list, board_size=6, delay=0.3)
```

### 出力
- 全ての組み合わせで対戦（N個のAIで N×(N-1) 試合）
- 最終順位表（勝ち点、勝敗、石数）

---

## 5. GitHubから投稿されたユーザーのmyai同士の総当たり戦

JSONLファイルからユーザーAIを読み込んで総当たり戦を行います。

```python
from battle import battle_user_ais

battle_user_ais('userdata/filtered_logs.jsonl', board_size=6, delay=0.3)
```

### 機能
- JSONLファイルから全てのユーザーAIを読み込み
- エラーのないAIのみを対戦させる
- 総当たり戦を実行
- 最終順位表を表示

---

## パラメータの詳細

### board_size
- `6`: 6x6の盤面（デフォルト）
- `8`: 8x8の盤面

### delay
- 各手の後の待機時間（秒）
- `0`: 待機なし（高速）
- `0.3`: 程よい速さ
- `0.5`: ゆっくり（デフォルト）
- `1.0`: かなりゆっくり

### width
- Canvasの幅（ピクセル）
- デフォルト: 300

---

## エラーハンドリング

- **無効な手**: 置けない場所に置こうとした場合、反則負けとなり石数は0個
- **例外発生**: AI内でエラーが発生した場合、石数は0個として扱う
- **思考時間**: 各AIの思考時間を計測して表示

---

## 対戦の様子を見る

### tqdmプログレスバー
対戦中はtqdmで進捗状況が表示されます：
```
対戦進行中:  44%|███████████████▊                 | 32/72 [00:03<00:04,  9.63it/s]
```

### リアルタイム盤面表示
- Canvas（kogi_canvas）でグラフィカルに盤面を表示
- 各手ごとに盤面が更新される
- 黒石 = 黒い円、白石 = 白い円

### 各手の情報
```
黒 🎓は(3, 1)におきました。黒: 4, 白: 1 (思考時間: 0.00123秒)
白 🤑は(4, 1)におきました。黒: 3, 白: 3 (思考時間: 0.00098秒)
```

---

## サンプル: 自分のmyai vs 友達のmyai

```python
# 1. リポジトリをクローン
!git clone https://github.com/me/othello2025.git my_ai
!git clone https://github.com/friend/othello2025.git friend_ai

# 2. インポート
from my_ai import myai as my_ai
from friend_ai import myai as friend_ai

# 3. 先攻・後攻入れ替えで2試合対戦
from battle import battle_myais_double
battle_myais_double(my_ai, friend_ai, name1="me", name2="friend", delay=0.3)
```

---

## 注意事項

1. **Jupyter/Colab環境**: Canvas表示はJupyter NotebookまたはGoogle Colabで動作します
2. **盤面サイズ**: myai関数は6x6と8x8の両方に対応している必要があります
3. **関数シグネチャ**: `myai(board, stone)` の形式で実装してください
   - `board`: 2次元リスト（盤面）
   - `stone`: 1 (黒) または 2 (白)
   - 戻り値: `(x, y)` タプル（0-indexed）
