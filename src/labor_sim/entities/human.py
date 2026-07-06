"""
Human：人類母體。
職責：持有能力分佈 self.a（向量化，never one-object-per-worker），
提供學習/再訓練的成長更新。不負責：任務生成、配對、指標計算。
"""

from __future__ import annotations
import numpy as np

from labor_sim.config import Config


class Human:
    def __init__(self, config: Config, rng: np.random.Generator):
        self.config = config
        # lognormal(0, sigma) 中位數為 1；乘 ability_median 後中位數 = ability_median
        self.a: np.ndarray = config.ability_median * rng.lognormal(
            mean=0.0, sigma=config.ability_sigma, size=config.n_workers
        )

    def grow(self, emp_mask: np.ndarray) -> None:
        """
        在崗者以 human_learning(g)、失業者以 retrain_rate 成長。
        ability_ceiling 有限 → 飽和式 a += growth*(ceiling-a)；否則舊行為：無上限複利 a *= (1+growth)。
        """
        p = self.config
        if p.human_learning > 0 or p.retrain_rate > 0:
            growth = np.where(emp_mask, p.human_learning, p.retrain_rate)
            if p.ability_ceiling is not None:
                self.a = self.a + growth * (p.ability_ceiling - self.a)
            else:
                self.a = self.a * (1.0 + growth)
