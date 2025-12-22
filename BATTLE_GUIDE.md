# オセロAI対戦システム - 使い方ガイド

`battle.py` を使って、オセロAI同士を対戦させる方法を説明します。

## 1. GitHubからクローンしたmyai同士の対戦（先攻・後攻2試合）

GitHubから2つのリポジトリをクローンして、それぞれの`myai`関数を対戦させます。
**先攻・後攻を入れ替えて2試合**行い、総合結果を表示します。

```python
# 1. メインリポジトリをクローン（battle.pyがここにある）
!git clone https://github.com/YuuhaNi/othello2025.git

# 2. 対戦相手のリポジトリをクローン
!git clone https://github.com/user1/othello2025.git a008
!git clone https://github.com/user2/othello2025.git a009

# 3. インポート
from a008 import myai as myai008
from a009 import myai as myai009
from othello2025 import battle_myais

# 4. 対戦させる（2試合）
battle_myais(myai008, myai009, name1="a008", name2="a009", delay=0.5)
```

### パラメータ
- `myai1`: 1つ目のmyai関数
- `myai2`: 2つ目のmyai関数
- `name1`: AI1の名前（表示用）
- `name2`: AI2の名前（表示用）
- `board_size`: 盤面サイズ（6 or 8、デフォルト: 6）
- `width`: Canvasの幅（デフォルト: 300）
- `delay`: 各手の後の待機時間（秒、デフォルト: 0.5）

### 出力
- 第1試合: myai1 (黒/先攻) vs myai2 (白/後攻)
- 第2試合: myai2 (黒/先攻) vs myai1 (白/後攻)
- リアルタイムで盤面が更新される（Canvas表示）
- 各手ごとに座標、石数、思考時間を表示
- 総合結果: 勝ち数、石数の合計、総合優勝者

---

## 2. カスタムmyai vs 既存AI

```python
from ai.greedy_ai import greedy_place
from a008 import myai as myai008

# myai vs 既存AI関数を2試合対戦
from battle import battle_myais
battle_myais(myai008, greedy_place, name1="a008", name2="greedy", delay=0.5)
```

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
!git clone https://github.com/YuuhaNi/othello2025.git
!git clone https://github.com/me/othello2025.git my_ai
!git clone https://github.com/friend/othello2025.git friend_ai

# 2. インポート
from my_ai import myai as my_ai
from friend_ai import myai as friend_ai
from othello2025 import battle_myais

# 3. 先攻・後攻入れ替えで2試合対戦
battle_myais(my_ai, friend_ai, name1="me", name2="friend", delay=0.3)
```

---

## 注意事項

1. **Jupyter/Colab環境**: Canvas表示はJupyter NotebookまたはGoogle Colabで動作します
2. **盤面サイズ**: myai関数は6x6と8x8の両方に対応している必要があります
3. **関数シグネチャ**: `myai(board, stone)` の形式で実装してください
   - `board`: 2次元リスト（盤面）
   - `stone`: 1 (黒) または 2 (白)
   - 戻り値: `(x, y)` タプル（0-indexed）
