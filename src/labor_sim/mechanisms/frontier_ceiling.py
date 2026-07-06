"""
FrontierCeilingMechanism：AI 前沿天花板的開關介面（L_0.3.0 新機制）。
掛鉤：pre_match——本步配對前，前沿 F 必須先推進到位（human_tasks 是否存在取決於 F）。

實際的 ceiling 數學（閉式解 vs 遞迴式的分支）活在 entities/matrix.py 的 Matrix.advance()，
這裡只是一層薄 wrapper：用 config.F_ceiling 是否為 None 來決定要不要啟用此機制物件，
讓「開/關天花板」在 config 只是改一個欄位（F_ceiling=None ↔ 有限值），不需要碰 world.py。

退化保證：F_ceiling=None 時 Matrix.advance() 內部走 F0+r*t 閉式解分支，
與 model.py 舊版逐位一致（見 entities/matrix.py 開頭註解）。
"""

from __future__ import annotations


class FrontierCeilingMechanism:
    def pre_match(self, world, t: int) -> None:
        world.matrix.advance(t)

    def post_step(self, world, t: int) -> None:
        pass  # no-op：ceiling 只影響前沿推進時機（pre_match），不影響配對後的收尾
