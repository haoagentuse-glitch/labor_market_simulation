"""
設定層：Config
==============
所有可調參數集中於此，欄位/預設值逐一對照 `model.py` 的 `Params`（零漂移前提）。
新增：`F_ceiling`（AI 前沿天花板，None = 舊行為 = 線性 F=F0+r*t）。
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Config:
    n_workers: int = 2000
    task_density: float = 2000.0  # 每單位 σ 的任務數（固定密度）→ 任務數隨 σ_max 等比成長
    steps: int = 240              # 月 × 20 年

    # --- 宏觀賽跑：前沿速度 vs 任務生成速度 ---
    F0: float = 0.20              # 初始前沿
    r: float = 0.003              # 前沿每步上升（速度；ceiling 有限時為趨近速率）
    sigma_max0: float = 1.0       # 初始任務上限
    c: float = 0.003              # 任務上限每步成長（新問題生成速度）

    # --- 分配結局：能力尾巴 × 價值凸度 ---
    ability_sigma: float = 0.5    # 能力 lognormal 的 sigma（尾巴重度）
    ability_median: float = 0.5   # 能力分佈中位數錨點
    V_curvature: float = 2.0      # V(sigma)=sigma^k 的 k

    # --- 其他 ---
    frontier_noise: float = 0.03  # 前沿毛邊 eps
    human_learning: float = 0.0   # g：在崗者能力緩升
    retrain_rate: float = 0.0     # 失業者再訓練時的能力成長

    # --- L_0.2.1 地基（預設 None = 舊行為，向後相容） ---
    tasks_per_worker: float | None = None
    ability_ceiling: float | None = None

    # --- L_0.3.0 新增：AI 前沿天花板 ---
    # None（預設）→ 閉式解 F = F0 + r*t（與舊版逐位一致，零漂移前提）。
    # 有限值   → 遞迴式 F_{t+1} = F_t + r*(1 - F_t/F_ceiling)，F_0 = F0（永不超過 ceiling）。
    F_ceiling: float | None = None

    seed: int = 0
