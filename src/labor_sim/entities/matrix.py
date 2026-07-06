"""
Matrix：AI 前沿。
職責：持有並推進前沿 F(t)。不負責：任務生成、配對、人類能力。

F ceiling 數學（L_0.3.0 新機制）：
  ceiling=None（預設）→ 閉式解 F = F0 + r*t —— 與舊版逐位一致（零漂移前提），
                         直接算,不透過遞迴,不引入額外浮點誤差來源。
  ceiling 有限        → 遞迴式 F_{t+1} = F_t + r*(1 - F_t/ceiling)，F_0 = F0。
                         dF/dt = r*(1-F/ceiling) → ceiling→∞ 退化回線性（研究動機見
                         docs/10_concept_v5_open-endgame.md §2.2）。
"""

from __future__ import annotations
import numpy as np

from labor_sim.config import Config


class Matrix:
    def __init__(self, config: Config):
        self.config = config
        self.ceiling = config.F_ceiling
        self.F = float(config.F0)          # 目前前沿值（遞迴式用；閉式解每步重算不依賴此狀態）
        self._t = 0

    def value_at(self, t: int) -> float:
        """回傳第 t 步的前沿值（不改變內部狀態，用於閉式解路徑）。"""
        p = self.config
        if self.ceiling is None:
            return p.F0 + p.r * t
        # 有限 ceiling：必須逐步遞迴到 t，不能跳算（保留給呼叫端用 advance() 累進）
        raise NotImplementedError("finite ceiling requires stepwise advance(); use advance(t)")

    def advance(self, t: int) -> float:
        """
        推進到第 t 步並回傳該步的 F。
        呼叫慣例：t 從 0 開始依序遞增呼叫（World 主迴圈保證）。
        - ceiling=None：直接回傳閉式解 F0+r*t（不依賴先前呼叫，任何順序都對，且與舊版位元一致）。
        - ceiling 有限：t=0 回傳 F0；t>0 用上一步的 self.F 遞迴一步。
        """
        p = self.config
        if self.ceiling is None:
            self.F = p.F0 + p.r * t
            return self.F
        if t == 0:
            self.F = p.F0
        else:
            self.F = self.F + p.r * (1.0 - self.F / self.ceiling)
        return self.F
