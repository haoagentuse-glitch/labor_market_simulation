"""
Mechanism 基底介面。
Hook 選型：pre_match(world, t) / post_step(world, t) 兩點掛鉤（而非單一 on_step）。
理由：本回合機制天然分兩種時機——
  - frontier_ceiling 屬於「本步開始前，前沿要先推進到位」→ pre_match。
  - learning 屬於「本步配對結果出來後，才知道誰在崗、才能決定成長」→ post_step。
單一 on_step 會逼世界迴圈把「前沿推進」與「配對」的次序寫死在 if-branch 裡判斷機制種類，
兩點掛鉤讓 World 主迴圈永遠是同一個固定順序：
  pre_match(所有機制) → market 生成任務/配對 → post_step(所有機制)。
未來加 demand.py 只需各自實作用得到的 hook（不需要的 hook 留預設 no-op），
World.run() 迴圈本體不必改一行。
"""

from __future__ import annotations
from typing import Protocol


class Mechanism(Protocol):
    def pre_match(self, world, t: int) -> None:
        """配對發生前的更新（例：推進前沿 F）。預設 no-op。"""
        ...

    def post_step(self, world, t: int) -> None:
        """配對完成、當步指標算好之後的更新（例：人類學習/再訓練）。預設 no-op。"""
        ...
