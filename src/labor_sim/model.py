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
    ability_median: float = 0.5   # 能力分佈中位數錨點（尺度校準，預設 0.5；僅敏感度檢查時掃描）
    V_curvature: float = 2.0      # V(sigma)=sigma^k 的 k

    # --- 其他 ---
    frontier_noise: float = 0.03  # 前沿毛邊 eps
    human_learning: float = 0.0   # g：在崗者能力緩升（宏觀體制決定者，見 v4 §0.5）
    retrain_rate: float = 0.0     # 失業者再訓練時的能力成長（第二個回饋，預設關）
    seed: int = 0


# 職業層級（用 σ 定義；v4 把「職業」收成單一 σ，這裡切成可解讀的層級）
OCC_EDGES = (0.4, 0.8, 1.2)       # 三條切線 → 四個就業層級
OCC_LABELS = ("失業", "低階 σ<0.4", "中階 0.4–0.8", "高階 0.8–1.2", "精英 σ>1.2")


# --------------------------------------------------------------------------- #
# 引擎
# --------------------------------------------------------------------------- #
@dataclass
class Result:
    params: Params
    F: np.ndarray
    sigma_max: np.ndarray
    employment_rate: np.ndarray
    gini: np.ndarray              # 全體 Gini（含失業者收入 0）—— 受就業水準汙染
    top10_share: np.ndarray
    human_zone: np.ndarray
    final_ability: np.ndarray
    # B-1：在職者 Gini（只算 earnings>0）—— 把集中度與就業水準分開。
    gini_employed: np.ndarray = field(default=None, repr=False)
    regime: str = ""
    history_earnings_last: np.ndarray = field(default=None, repr=False)

    # --- 過程／機制量（解釋因果用） ---
    # 圖一：職業結構變化
    occ_shares: np.ndarray = field(default=None, repr=False)      # (steps, 5) 各層級人口比例
    ai_substitution: np.ndarray = field(default=None, repr=False) # AI 替代率（任務價值佔比）
    new_job_rate: np.ndarray = field(default=None, repr=False)    # 新職業生成率（σ>σ_max0 的價值佔比）
    # 圖二：技能演化
    mean_ability: np.ndarray = field(default=None, repr=False)        # 全體平均技能
    mean_ability_emp: np.ndarray = field(default=None, repr=False)    # 在崗者平均技能
    retrain_success: np.ndarray = field(default=None, repr=False)     # 再訓練成功率
    demand_median: np.ndarray = field(default=None, repr=False)       # 技能需求（人類任務 σ 中位）
    supply_median: np.ndarray = field(default=None, repr=False)       # 技能供給（worker a 中位）
    unmet_demand: np.ndarray = field(default=None, repr=False)        # 未填補的人類任務比例
    unused_supply: np.ndarray = field(default=None, repr=False)       # 閒置人力（失業）比例


def _make_ability(p: Params, rng) -> np.ndarray:
    """
    能力分佈：lognormal，中位數錨定在 0.5，使前沿 F（約 0.2→0.9）掃過分佈主體。
    ability_sigma 控制尾巴重度（同時左右散開，重尾＝少數人遠高、多數人偏低）。
    """
    # lognormal(0, sigma) 的中位數為 1；乘 ability_median 後中位數 = ability_median（預設 0.5）
    return p.ability_median * rng.lognormal(mean=0.0, sigma=p.ability_sigma, size=p.n_workers)


def _match(a: np.ndarray, sigma_tasks: np.ndarray, k: float):
    """
    排序匹配（assortative，貪婪，O(n log n)）：
    任務由大到小、worker 由大到小，能做就配；做不動的任務沒人能做就留空。
    回傳 (earnings, assigned_sigma, n_filled)：
      earnings        每個 worker 的收入（未配到者為 0）
      assigned_sigma  每個 worker 接到的任務 σ（未配到者為 -1）—— 用來分職業層級
      n_filled        被填補的人類任務數

    集中不靠 O-ring 塞進來——它若出現，是排序 + 重尾 + 凸 V 的後果。
    """
    n = a.size
    earnings = np.zeros(n)
    assigned = np.full(n, -1.0)
    if sigma_tasks.size == 0:
        return earnings, assigned, 0

    tasks_desc = np.sort(sigma_tasks)[::-1]
    order = np.argsort(a)[::-1]        # worker 由大到小的原始索引
    a_desc = a[order]

    wi = 0
    for tsig in tasks_desc:
        if wi >= n:
            break                      # 全員就業
        if a_desc[wi] >= tsig:         # 最大的可用 worker 能做這個最大的任務
            earnings[order[wi]] = tsig ** k
            assigned[order[wi]] = tsig
            wi += 1
        # 否則：最大剩餘 worker 都做不動 → 此任務沒人能做，換下一個（較小）任務
    return earnings, assigned, wi


def run_sim(p: Params | None = None, **kw) -> Result:
    if p is None:
        p = Params(**kw)
    rng = np.random.default_rng(p.seed)

    a = _make_ability(p, rng)

    S = p.steps
    F_hist = np.empty(S); smax_hist = np.empty(S)
    emp_hist = np.empty(S); gini_hist = np.empty(S)
    gini_emp_hist = np.empty(S)        # B-1：在職者 Gini
    top_hist = np.empty(S); zone_hist = np.empty(S)
    # 過程量
    occ_hist = np.zeros((S, 5))
    ai_sub_hist = np.empty(S); newjob_hist = np.empty(S)
    mean_a_hist = np.empty(S); mean_a_emp_hist = np.empty(S)
    retrain_hist = np.zeros(S)
    demand_hist = np.empty(S); supply_hist = np.empty(S)
    unmet_hist = np.empty(S); unused_hist = np.empty(S)

    last_earn = np.zeros(p.n_workers)
    prev_emp_mask = np.zeros(p.n_workers, dtype=bool)   # 上一步是否就業（算再訓練成功率）
    k = p.V_curvature

    for t in range(S):
        F = p.F0 + p.r * t
        sigma_max = p.sigma_max0 + p.c * t

        # 本步任務：固定密度 → 任務數隨 sigma_max 等比成長，使 r=c 時人類區工作量中性
        n_tasks_t = max(1, int(round(p.task_density * sigma_max)))
        sigma = rng.uniform(0.0, sigma_max, size=n_tasks_t)

        # 毛邊前沿：每個任務的有效門檻 = F + 雜訊
        thresh = F + rng.normal(0.0, p.frontier_noise, size=n_tasks_t)
        ai_mask = sigma < thresh                  # AI 獨力完成（替代）
        human_tasks = sigma[~ai_mask]             # 需要人的任務（前沿以上）

        earn, assigned, n_filled = _match(a, human_tasks, k)
        last_earn = earn
        emp_mask = earn > 0

        # --- 基本指標 ---
        F_hist[t] = F
        smax_hist[t] = sigma_max
        emp_hist[t] = float(emp_mask.mean())
        gini_hist[t] = gini(earn)
        # 在職者 Gini：只在賺到錢的人之間算，去掉失業者一堆 0 對集中度的汙染。
        gini_emp_hist[t] = gini(earn[emp_mask]) if emp_mask.any() else np.nan
        top_hist[t] = top_share(earn, 0.10)
        zone_hist[t] = max(sigma_max - F, 0.0)

        # --- 圖一：職業結構 ---
        # 各層級人口比例（失業 + 四個 σ 層級）
        occ_hist[t, 0] = 1.0 - emp_mask.mean()
        if emp_mask.any():
            tiers = np.digitize(assigned[emp_mask], OCC_EDGES)   # 0..3
            for i in range(4):
                occ_hist[t, i + 1] = np.count_nonzero(tiers == i) / p.n_workers
        # AI 替代率（以任務價值 σ^k 加權）
        all_val = np.sum(sigma ** k)
        ai_sub_hist[t] = float(np.sum(sigma[ai_mask] ** k) / all_val) if all_val > 0 else 0.0
        # 新職業生成率（σ 超過初始上限 σ_max0 的價值佔比）
        newjob_hist[t] = float(np.sum(sigma[sigma > p.sigma_max0] ** k) / all_val) if all_val > 0 else 0.0

        # --- 圖二：技能演化 ---
        mean_a_hist[t] = float(a.mean())
        mean_a_emp_hist[t] = float(a[emp_mask].mean()) if emp_mask.any() else np.nan
        # 再訓練成功率：上一步失業、這一步就業的比例（t=0 無前一步，留 0）
        if t > 0 and (~prev_emp_mask).any():
            recovered = np.count_nonzero(emp_mask & ~prev_emp_mask)
            retrain_hist[t] = recovered / np.count_nonzero(~prev_emp_mask)
        # 技能需求 vs 供給
        demand_hist[t] = float(np.median(human_tasks)) if human_tasks.size else F
        supply_hist[t] = float(np.median(a))
        unmet_hist[t] = float(1.0 - n_filled / human_tasks.size) if human_tasks.size else 0.0
        unused_hist[t] = occ_hist[t, 0]

        prev_emp_mask = emp_mask

        # --- 回饋：在崗者學習(g) / 失業者再訓練(retrain_rate) ---
        if p.human_learning > 0 or p.retrain_rate > 0:
            growth = np.where(emp_mask, p.human_learning, p.retrain_rate)
            a = a * (1.0 + growth)

    res = Result(
        params=p,
        F=F_hist, sigma_max=smax_hist,
        employment_rate=emp_hist, gini=gini_hist,
        top10_share=top_hist, human_zone=zone_hist,
        final_ability=a, history_earnings_last=last_earn,
        gini_employed=gini_emp_hist,
        occ_shares=occ_hist, ai_substitution=ai_sub_hist, new_job_rate=newjob_hist,
        mean_ability=mean_a_hist, mean_ability_emp=mean_a_emp_hist,
        retrain_success=retrain_hist,
        demand_median=demand_hist, supply_median=supply_hist,
        unmet_demand=unmet_hist, unused_supply=unused_hist,
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
              f"gini_emp={res.gini_employed[-1]:.2f} "
              f"top10={res.top10_share[-1]:.2f} "
              f"zone={res.human_zone[-1]:.2f}")
