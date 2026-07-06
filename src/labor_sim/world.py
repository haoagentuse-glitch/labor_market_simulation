"""
World：一個時間步的編排者。
職責：持有三實體（Human/Matrix/Market）+ 啟用機制清單，跑主迴圈，收集全部指標，
回傳等價於舊 Result 的 dataclass（多一個 labor_share 欄位）。不負責：機制內部邏輯、
指標公式本身（委派給 metrics.py）。

主迴圈固定順序（未來加機制只需要多一個 mechanisms 清單項，不改這裡）：
  for t in range(steps):
      pre_match(所有機制, t)      # 例：推進前沿 F
      market 生成任務 → AI/人類分流 → 排序匹配
      記錄當步全部指標
      post_step(所有機制, t)      # 例：人類學習/再訓練
"""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

from labor_sim.config import Config
from labor_sim.metrics import gini, top_share, labor_share, OCC_EDGES
from labor_sim.entities.human import Human
from labor_sim.entities.matrix import Matrix
from labor_sim.entities.market import Market
from labor_sim.mechanisms.learning import LearningMechanism
from labor_sim.mechanisms.frontier_ceiling import FrontierCeilingMechanism


@dataclass
class WorldResult:
    config: Config
    F: np.ndarray
    sigma_max: np.ndarray
    employment_rate: np.ndarray
    gini: np.ndarray
    top10_share: np.ndarray
    human_zone: np.ndarray
    final_ability: np.ndarray
    gini_employed: np.ndarray = field(default=None, repr=False)
    regime: str = ""
    history_earnings_last: np.ndarray = field(default=None, repr=False)

    occ_shares: np.ndarray = field(default=None, repr=False)
    ai_substitution: np.ndarray = field(default=None, repr=False)
    new_job_rate: np.ndarray = field(default=None, repr=False)
    mean_ability: np.ndarray = field(default=None, repr=False)
    mean_ability_emp: np.ndarray = field(default=None, repr=False)
    retrain_success: np.ndarray = field(default=None, repr=False)
    demand_median: np.ndarray = field(default=None, repr=False)
    supply_median: np.ndarray = field(default=None, repr=False)
    unmet_demand: np.ndarray = field(default=None, repr=False)
    unused_supply: np.ndarray = field(default=None, repr=False)

    # L_0.3.0 新增
    labor_share: np.ndarray = field(default=None, repr=False)
    near_frontier_share: np.ndarray = field(default=None, repr=False)  # 接到 σ∈[F,F+0.2] 任務的人口比例（中介職業帶）

    # 為向後相容保留 params 別名（部分舊程式碼可能用 res.params）
    @property
    def params(self) -> Config:
        return self.config


class World:
    def __init__(self, config: Config):
        self.config = config
        self.rng = np.random.default_rng(config.seed)

        self.human = Human(config, self.rng)
        self.matrix = Matrix(config)
        self.market = Market(config)

        self.mechanisms = [FrontierCeilingMechanism(), LearningMechanism()]

        # 當步暫存（機制之間、World 之間溝通用）
        self.last_emp_mask: np.ndarray = np.zeros(config.n_workers, dtype=bool)

    def run(self) -> WorldResult:
        p = self.config
        S = p.steps
        k = p.V_curvature

        F_hist = np.empty(S); smax_hist = np.empty(S)
        emp_hist = np.empty(S); gini_hist = np.empty(S)
        gini_emp_hist = np.empty(S)
        top_hist = np.empty(S); zone_hist = np.empty(S)
        occ_hist = np.zeros((S, 5))
        ai_sub_hist = np.empty(S); newjob_hist = np.empty(S)
        mean_a_hist = np.empty(S); mean_a_emp_hist = np.empty(S)
        retrain_hist = np.zeros(S)
        demand_hist = np.empty(S); supply_hist = np.empty(S)
        unmet_hist = np.empty(S); unused_hist = np.empty(S)
        labor_share_hist = np.empty(S)
        near_frontier_hist = np.zeros(S)
        NEAR_BAND = 0.2                     # 中介職業帶寬：接到 σ∈[F, F+0.2] 任務者

        last_earn = np.zeros(p.n_workers)
        prev_emp_mask = np.zeros(p.n_workers, dtype=bool)

        for t in range(S):
            # --- pre_match：目前只有 frontier_ceiling 用到，推進 F ---
            for m in self.mechanisms:
                m.pre_match(self, t)
            F = self.matrix.F
            sigma_max = self.market.sigma_max_at(t)

            # --- market：生成任務、AI/人類分流、排序匹配 ---
            sigma = self.market.generate_tasks(t, self.rng)
            ai_mask, human_tasks = self.market.split_ai_human(sigma, F, self.rng)
            earn, assigned, n_filled = Market.match(self.human.a, human_tasks, k)
            last_earn = earn
            emp_mask = earn > 0
            self.last_emp_mask = emp_mask

            # --- 基本指標 ---
            F_hist[t] = F
            smax_hist[t] = sigma_max
            emp_hist[t] = float(emp_mask.mean())
            gini_hist[t] = gini(earn)
            gini_emp_hist[t] = gini(earn[emp_mask]) if emp_mask.any() else np.nan
            top_hist[t] = top_share(earn, 0.10)
            zone_hist[t] = max(sigma_max - F, 0.0)
            labor_share_hist[t] = labor_share(earn, sigma, k)
            if emp_mask.any():
                near_frontier_hist[t] = float(
                    np.count_nonzero(emp_mask & (assigned >= F) & (assigned <= F + NEAR_BAND)) / p.n_workers
                )

            # --- 職業結構 ---
            occ_hist[t, 0] = 1.0 - emp_mask.mean()
            if emp_mask.any():
                tiers = np.digitize(assigned[emp_mask], OCC_EDGES)
                for i in range(4):
                    occ_hist[t, i + 1] = np.count_nonzero(tiers == i) / p.n_workers
            all_val = np.sum(sigma ** k)
            ai_sub_hist[t] = float(np.sum(sigma[ai_mask] ** k) / all_val) if all_val > 0 else 0.0
            newjob_hist[t] = float(np.sum(sigma[sigma > p.sigma_max0] ** k) / all_val) if all_val > 0 else 0.0

            # --- 技能演化 ---
            mean_a_hist[t] = float(self.human.a.mean())
            mean_a_emp_hist[t] = float(self.human.a[emp_mask].mean()) if emp_mask.any() else np.nan
            if t > 0 and (~prev_emp_mask).any():
                recovered = np.count_nonzero(emp_mask & ~prev_emp_mask)
                retrain_hist[t] = recovered / np.count_nonzero(~prev_emp_mask)
            demand_hist[t] = float(np.median(human_tasks)) if human_tasks.size else F
            supply_hist[t] = float(np.median(self.human.a))
            unmet_hist[t] = float(1.0 - n_filled / human_tasks.size) if human_tasks.size else 0.0
            unused_hist[t] = occ_hist[t, 0]

            prev_emp_mask = emp_mask

            # --- post_step：目前只有 learning 用到，人類成長 ---
            for m in self.mechanisms:
                m.post_step(self, t)

        res = WorldResult(
            config=p,
            F=F_hist, sigma_max=smax_hist,
            employment_rate=emp_hist, gini=gini_hist,
            top10_share=top_hist, human_zone=zone_hist,
            final_ability=self.human.a, history_earnings_last=last_earn,
            gini_employed=gini_emp_hist,
            occ_shares=occ_hist, ai_substitution=ai_sub_hist, new_job_rate=newjob_hist,
            mean_ability=mean_a_hist, mean_ability_emp=mean_a_emp_hist,
            retrain_success=retrain_hist,
            demand_median=demand_hist, supply_median=supply_hist,
            unmet_demand=unmet_hist, unused_supply=unused_hist,
            labor_share=labor_share_hist,
            near_frontier_share=near_frontier_hist,
        )
        res.regime = classify_regime(res)
        return res


def classify_regime(res: WorldResult) -> str:
    """
    order parameter 客觀分類，檢查順序固定、first-match-wins：
      1. collapse       ：人類區關閉 或 末段就業腰斬 或 tail<0.25
      2. human_premium  ：ceiling 有限 且 前沿末段增速 <0.1r 且 末段就業>=0.6 且 末段人類區>0
      3. concentration  ：top10 末段均值 >0.5
      4. reallocation   ：其餘
    """
    emp = res.employment_rate
    tail = emp[-12:].mean()
    head = emp[:12].mean()
    zone_closed = res.human_zone[-1] <= 1e-9
    top = res.top10_share[-12:].mean()

    if zone_closed or (head > 0 and tail < 0.5 * head) or tail < 0.25:
        return "collapse"

    ceiling = res.config.F_ceiling
    if ceiling is not None:
        r = res.config.r
        dF_dt = (res.F[-1] - res.F[-13]) / 12.0
        zone_tail = res.human_zone[-12:].mean()
        if dF_dt < 0.1 * r and tail >= 0.6 and zone_tail > 0:
            return "human_premium"

    if top > 0.50:
        return "concentration"
    return "reallocation"


def run_sim(config: Config | None = None, **kw) -> WorldResult:
    """便利函數：一行跑完一個情境。"""
    if config is None:
        config = Config(**kw)
    return World(config).run()
