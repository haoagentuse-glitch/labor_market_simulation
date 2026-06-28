"""
最小核心引擎 v4：三純量 + 一條規則
=====================================

三個純量：
    task : sigma  —— 任務離 AI 前沿多遠（＝需要多少「賦予結構」的能力）
    人   : a      —— 能力，異質分佈（尾巴形狀可掃描）
    AI   : F(t)   —— 前沿，隨時間以速度 r 上爬

一條規則（每步、每個任務）：
    sigma < F - eps  → AI 獨力完成（替代）
    sigma >= F       → 需要 a >= sigma 的人來賦予結構，產出 V(sigma)=sigma^k
                       合格者裡能力高的配 sigma 高的（排序匹配）
    a 一直 < F 的人   → 失業

替代、協作、逃跑賽跑、集中/壓縮全部從這條規則「浮現」，沒有任何一個被設定。
"""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


# --------------------------------------------------------------------------- #
# 指標
# --------------------------------------------------------------------------- #
def gini(x: np.ndarray) -> float:
    """Gini 係數，定義在所有人（含失業者，收入 0）上。"""
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return 0.0
    if np.all(x == 0):
        return 0.0
    x = np.sort(x)
    n = x.size
    idx = np.arange(1, n + 1)
    # 標準 Gini 公式
    return float((2.0 * np.sum(idx * x) / (n * np.sum(x))) - (n + 1.0) / n)


def top_share(x: np.ndarray, q: float = 0.10) -> float:
    """頂端 q 比例的人賺走多少份額（衡量集中度）。"""
    x = np.asarray(x, dtype=float)
    total = x.sum()
    if total <= 0:
        return 0.0
    k = max(1, int(round(x.size * q)))
    return float(np.sort(x)[-k:].sum() / total)


# --------------------------------------------------------------------------- #
# 參數
# --------------------------------------------------------------------------- #
@dataclass
class Params:
    n_workers: int = 2000
    task_density: float = 2000.0  # 每單位 σ 的任務數（固定密度）→ 任務數隨 σ_max 等比成長
    steps: int = 240              # 月 × 20 年

    # --- 宏觀賽跑：前沿速度 vs 任務生成速度 ---
    F0: float = 0.20              # 初始前沿
    r: float = 0.003             # 前沿每步上升
    sigma_max0: float = 1.0       # 初始任務上限
    c: float = 0.003             # 任務上限每步成長（新問題生成速度）

    # --- 分配結局：能力尾巴 × 價值凸度 ---
    ability_sigma: float = 0.5    # 能力 lognormal 的 sigma（尾巴重度）
    V_curvature: float = 2.0      # V(sigma)=sigma^k 的 k

    # --- 其他 ---
    frontier_noise: float = 0.03  # 前沿毛邊 eps
    human_learning: float = 0.0   # 可選：在崗者能力緩升（預設關，屬後續回饋）
    seed: int = 0


# --------------------------------------------------------------------------- #
# 引擎
# --------------------------------------------------------------------------- #
@dataclass
class Result:
    params: Params
    F: np.ndarray
    sigma_max: np.ndarray
    employment_rate: np.ndarray
    gini: np.ndarray
    top10_share: np.ndarray
    human_zone: np.ndarray
    final_ability: np.ndarray
    regime: str = ""
    history_earnings_last: np.ndarray = field(default=None, repr=False)


def _make_ability(p: Params, rng) -> np.ndarray:
    """
    能力分佈：lognormal，中位數錨定在 0.5，使前沿 F（約 0.2→0.9）掃過分佈主體。
    ability_sigma 控制尾巴重度（同時左右散開，重尾＝少數人遠高、多數人偏低）。
    """
    # lognormal(0, sigma) 的中位數為 1；乘 0.5 後中位數 = 0.5
    return 0.5 * rng.lognormal(mean=0.0, sigma=p.ability_sigma, size=p.n_workers)


def _match(a: np.ndarray, sigma_tasks: np.ndarray, k: float) -> np.ndarray:
    """
    排序匹配（assortative，貪婪，O(n log n)）：
    任務由大到小、worker 由大到小，能做就配；做不動的任務沒人能做就留空。
    回傳每個 worker 的 earnings（未配到者為 0）。

    集中不靠 O-ring 塞進來——它若出現，是排序 + 重尾 + 凸 V 的後果。
    """
    n = a.size
    earnings = np.zeros(n)
    if sigma_tasks.size == 0:
        return earnings

    tasks_desc = np.sort(sigma_tasks)[::-1]
    order = np.argsort(a)[::-1]        # worker 由大到小的原始索引
    a_desc = a[order]

    wi = 0
    for tsig in tasks_desc:
        if wi >= n:
            break                      # 全員就業
        if a_desc[wi] >= tsig:         # 最大的可用 worker 能做這個最大的任務
            earnings[order[wi]] = tsig ** k
            wi += 1
        # 否則：最大剩餘 worker 都做不動 → 此任務沒人能做，換下一個（較小）任務
    return earnings


def run_sim(p: Params | None = None, **kw) -> Result:
    if p is None:
        p = Params(**kw)
    rng = np.random.default_rng(p.seed)

    a = _make_ability(p, rng)

    F_hist = np.empty(p.steps)
    smax_hist = np.empty(p.steps)
    emp_hist = np.empty(p.steps)
    gini_hist = np.empty(p.steps)
    top_hist = np.empty(p.steps)
    zone_hist = np.empty(p.steps)
    last_earn = np.zeros(p.n_workers)

    for t in range(p.steps):
        F = p.F0 + p.r * t
        sigma_max = p.sigma_max0 + p.c * t

        # 本步任務：固定密度 → 任務數隨 sigma_max 等比成長，使 r=c 時人類區工作量中性
        n_tasks_t = max(1, int(round(p.task_density * sigma_max)))
        sigma = rng.uniform(0.0, sigma_max, size=n_tasks_t)

        # 毛邊前沿：每個任務的有效門檻 = F + 雜訊
        thresh = F + rng.normal(0.0, p.frontier_noise, size=p.n_tasks)
        human_tasks = sigma[sigma >= thresh]      # 需要人的任務（前沿以上）
        # 其餘 sigma < thresh 的任務由 AI 獨力完成（替代），不需配人

        earn = _match(a, human_tasks, p.V_curvature)
        last_earn = earn

        F_hist[t] = F
        smax_hist[t] = sigma_max
        emp_hist[t] = float((earn > 0).mean())
        gini_hist[t] = gini(earn)
        top_hist[t] = top_share(earn, 0.10)
        zone_hist[t] = max(sigma_max - F, 0.0)

        # 可選回饋：在崗者能力緩升（預設關）
        if p.human_learning > 0:
            a = np.where(earn > 0, a * (1.0 + p.human_learning), a)

    res = Result(
        params=p,
        F=F_hist, sigma_max=smax_hist,
        employment_rate=emp_hist, gini=gini_hist,
        top10_share=top_hist, human_zone=zone_hist,
        final_ability=a, history_earnings_last=last_earn,
    )
    res.regime = classify_regime(res)
    return res


def classify_regime(res: Result) -> str:
    """
    用 order parameter 客觀分類，不靠眼睛看：
      - 人類區關閉 或 末段就業相對初期腰斬 → collapse（崩潰）
      - 否則頂端份額很高               → concentration（集中）
      - 否則                          → reallocation（重配置）
    """
    emp = res.employment_rate
    tail = emp[-12:].mean()                 # 最後一年平均
    head = emp[:12].mean()                  # 第一年平均
    zone_closed = res.human_zone[-1] <= 1e-9
    top = res.top10_share[-12:].mean()

    if zone_closed or (head > 0 and tail < 0.5 * head) or tail < 0.25:
        return "collapse"
    if top > 0.50:
        return "concentration"
    return "reallocation"


if __name__ == "__main__":
    # 快速冒煙測試：印三種情境的末段指標
    scenarios = {
        "collapse  r>>g": dict(r=0.005, human_learning=0.000),
        "tug-of-war r~g": dict(r=0.004, human_learning=0.004),
        "realloc   g>=r": dict(r=0.003, human_learning=0.006),
    }
    for name, kw in scenarios.items():
        res = run_sim(Params(**kw))
        print(f"{name:22s} | regime={res.regime:13s} "
              f"emp={res.employment_rate[-1]:.2f} "
              f"gini={res.gini[-1]:.2f} "
              f"top10={res.top10_share[-1]:.2f} "
              f"zone={res.human_zone[-1]:.2f}")
