"""
兩張相圖（v4 的主要交付物）。
    uv run python scripts/sweep.py
輸出：
    figures/phase_macro.png        宏觀賽跑：(r, g) → 末段就業率 + 體制
    figures/phase_distribution.png 分配結局：(ability_sigma, k) → 頂端 10% 份額

每格多種子平均，降低雜訊。格數可調（GRID）。
"""

from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from labor_sim.model import Params, run_sim, classify_regime
from labor_sim.plotutil import setup_cjk_font

setup_cjk_font()

# figures/ 固定指向 repo 根
FIGDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIGDIR, exist_ok=True)

GRID = 13          # 每軸格數（先小一點求快，要細再加）
SEEDS = 3          # 每格平均的種子數


def _avg(metric_fn, base_kw, seeds=SEEDS):
    vals = []
    for s in range(seeds):
        res = run_sim(Params(seed=s, **base_kw))
        vals.append(metric_fn(res))
    return float(np.mean(vals))


def phase_macro():
    """
    宏觀賽跑：前沿速度 r vs 人類學習速度 g → 崩潰 / 重配置。
    （實作發現：靜態能力下 c 救不了被替代者，真正切換體制的是 r vs g。）
    """
    rs = np.linspace(0.001, 0.007, GRID)
    gs = np.linspace(0.000, 0.008, GRID)     # 人類學習速度
    emp = np.zeros((GRID, GRID))
    for i, g in enumerate(gs):               # 列：g
        for j, r in enumerate(rs):           # 行：r
            emp[i, j] = _avg(lambda R: R.employment_rate[-12:].mean(),
                             dict(r=r, human_learning=g))

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(emp, origin="lower", aspect="auto", cmap="RdYlGn",
                   vmin=0, vmax=1,
                   extent=[rs[0], rs[-1], gs[0], gs[-1]])
    lo, hi = max(rs[0], gs[0]), min(rs[-1], gs[-1])
    ax.plot([lo, hi], [lo, hi], "k--", lw=1.5, label="r = g（賽跑臨界線）")
    ax.set_xlabel("前沿上升速度 r")
    ax.set_ylabel("人類學習速度 g")
    ax.set_title("宏觀相圖：末段就業率\n（綠=重配置存活，紅=結構性崩潰）")
    ax.legend(loc="lower right", fontsize=8)
    fig.colorbar(im, ax=ax, label="末段就業率")
    fig.tight_layout()
    out = os.path.join(FIGDIR, "phase_macro.png")
    fig.savefig(out, dpi=120)
    print(f"已存圖：{out}")


def phase_distribution():
    """分配：能力尾巴 ability_sigma vs 價值凸度 k → 集中 / 壓縮。"""
    sigmas = np.linspace(0.2, 1.2, GRID)     # 能力尾巴重度
    ks = np.linspace(0.5, 3.0, GRID)         # V(σ)=σ^k 凸度
    top = np.zeros((GRID, GRID))
    for i, k in enumerate(ks):               # 列：k
        for j, sg in enumerate(sigmas):      # 行：sigma
            top[i, j] = _avg(lambda R: R.top10_share[-12:].mean(),
                             dict(ability_sigma=sg, V_curvature=k))

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(top, origin="lower", aspect="auto", cmap="magma",
                   vmin=0.1, vmax=1.0,
                   extent=[sigmas[0], sigmas[-1], ks[0], ks[-1]])
    ax.set_xlabel("能力尾巴重度 ability_sigma")
    ax.set_ylabel("價值凸度 k（V=σ^k）")
    ax.set_title("分配相圖：頂端 10% 收入份額\n（亮=超級明星集中，暗=壓縮）")
    fig.colorbar(im, ax=ax, label="頂端 10% 份額")
    fig.tight_layout()
    out = os.path.join(FIGDIR, "phase_distribution.png")
    fig.savefig(out, dpi=120)
    print(f"已存圖：{out}")


if __name__ == "__main__":
    print(f"掃描中（GRID={GRID}, SEEDS={SEEDS}，約 {GRID*GRID*SEEDS*2} 次模擬）…")
    phase_macro()
    phase_distribution()
    print("完成。")
