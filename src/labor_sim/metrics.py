"""
指標層：gini / top_share / labor_share 與職業層級定義。
與 model.py 的定義逐位一致（零漂移前提）。
"""

from __future__ import annotations
import numpy as np


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
    return float((2.0 * np.sum(idx * x) / (n * np.sum(x))) - (n + 1.0) / n)


def top_share(x: np.ndarray, q: float = 0.10) -> float:
    """頂端 q 比例的人賺走多少份額（衡量集中度）。"""
    x = np.asarray(x, dtype=float)
    total = x.sum()
    if total <= 0:
        return 0.0
    k = max(1, int(round(x.size * q)))
    return float(np.sort(x)[-k:].sum() / total)


def labor_share(earnings: np.ndarray, all_tasks_sigma: np.ndarray, k: float) -> float:
    """
    勞動所得份額 = Σ(實際發生的 earnings，即已配對人類任務的 σ^k) / Σ V(σ) over 全部任務。
    分母＝當步「全部」任務（含未填補的人類任務、含被 AI 拿走的任務），不是 1 減替代率。
    """
    all_val = np.sum(all_tasks_sigma ** k)
    if all_val <= 0:
        return 0.0
    return float(np.sum(earnings) / all_val)


# 職業層級（用 σ 定義；四條切線 → 五個就業層級：失業 + 四級）
OCC_EDGES = (0.4, 0.8, 1.2)
OCC_LABELS = ("失業", "低階 σ<0.4", "中階 0.4–0.8", "高階 0.8–1.2", "精英 σ>1.2")
