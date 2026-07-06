"""
Market：任務生成 + 排序匹配。
職責：每步生成任務 σ 分佈、依前沿門檻分流 AI/人類任務、將人類任務貪婪排序匹配給人。
不負責：前沿推進、人類能力更新。
"""

from __future__ import annotations
import numpy as np

from labor_sim.config import Config


class Market:
    def __init__(self, config: Config):
        self.config = config
        # L_0.2.1 槽位校準：若指定 tasks_per_worker，反推 task_density
        # 使 t=0 人類任務數 ≈ tasks_per_worker × n_workers。未指定則沿用 config.task_density。
        self.task_density = config.task_density
        if config.tasks_per_worker is not None:
            span0 = max(1e-9, config.sigma_max0 - config.F0)
            self.task_density = config.tasks_per_worker * config.n_workers / span0

    def sigma_max_at(self, t: int) -> float:
        p = self.config
        return p.sigma_max0 + p.c * t

    def generate_tasks(self, t: int, rng: np.random.Generator) -> np.ndarray:
        """本步任務 σ：固定密度 → 任務數隨 sigma_max 等比成長。"""
        sigma_max = self.sigma_max_at(t)
        n_tasks_t = max(1, int(round(self.task_density * sigma_max)))
        return rng.uniform(0.0, sigma_max, size=n_tasks_t)

    def split_ai_human(self, sigma: np.ndarray, F: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        """毛邊前沿：每個任務的有效門檻 = F + 雜訊。回傳 (ai_mask, human_tasks_sigma)。"""
        p = self.config
        thresh = F + rng.normal(0.0, p.frontier_noise, size=sigma.size)
        ai_mask = sigma < thresh
        human_tasks = sigma[~ai_mask]
        return ai_mask, human_tasks

    @staticmethod
    def match(a: np.ndarray, sigma_tasks: np.ndarray, k: float):
        """
        排序匹配（assortative，貪婪，O(n log n)）：與 model.py 的 _match 邏輯完全相同。
        回傳 (earnings, assigned_sigma, n_filled)。
        """
        n = a.size
        earnings = np.zeros(n)
        assigned = np.full(n, -1.0)
        if sigma_tasks.size == 0:
            return earnings, assigned, 0

        tasks_desc = np.sort(sigma_tasks)[::-1]
        order = np.argsort(a)[::-1]
        a_desc = a[order]

        wi = 0
        for tsig in tasks_desc:
            if wi >= n:
                break
            if a_desc[wi] >= tsig:
                earnings[order[wi]] = tsig ** k
                assigned[order[wi]] = tsig
                wi += 1
        return earnings, assigned, wi
