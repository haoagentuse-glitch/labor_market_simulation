"""
基線與三情境：時間序列圖。
    uv run python scripts/run.py
輸出 figures/baseline_timeseries.png 與終端機指標。
"""

from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")          # 無顯示環境，直接存檔
import matplotlib.pyplot as plt
import numpy as np

from labor_sim.model import Params, run_sim
from labor_sim.plotutil import setup_cjk_font

setup_cjk_font()

# figures/ 固定指向 repo 根，無論從哪個 cwd 執行
FIGDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIGDIR, exist_ok=True)


# 實作後的發現：靜態能力下，前沿 F 掃過固定能力分佈會讓所有低於 F 的人失業，
# 而任務生成 c 只在前沿「之上」加任務（只有高能力者能接），救不了被替代者。
# 真正切換「崩潰 ↔ 重配置」的是「人類適應速度 g（學習）」與前沿速度 r 的賽跑。
SCENARIOS = {
    "崩潰 r≫g (無學習)":  dict(r=0.005, human_learning=0.000),
    "拉鋸 r≈g":          dict(r=0.004, human_learning=0.004),
    "重配置 g≥r":        dict(r=0.003, human_learning=0.006),
}


def main():
    results = {name: run_sim(Params(**kw)) for name, kw in SCENARIOS.items()}

    # 終端機摘要
    print(f"{'情境':12s} {'regime':14s} {'emp':>5s} {'gini':>5s} {'top10':>6s} {'zone':>5s}")
    for name, res in results.items():
        print(f"{name:12s} {res.regime:14s} "
              f"{res.employment_rate[-1]:5.2f} {res.gini[-1]:5.2f} "
              f"{res.top10_share[-1]:6.2f} {res.human_zone[-1]:5.2f}")

    # 圖：四面板 × 三情境
    months = np.arange(next(iter(results.values())).employment_rate.size)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    panels = [
        ("employment_rate", "就業率 employment", axes[0, 0]),
        ("human_zone",      "人類保護區寬度 σ_max−F", axes[0, 1]),
        ("gini",            "Gini（含失業者）", axes[1, 0]),
        ("top10_share",     "頂端 10% 收入份額", axes[1, 1]),
    ]
    for attr, title, ax in panels:
        for name, res in results.items():
            ax.plot(months, getattr(res, attr), label=name, lw=2)
        ax.set_title(title)
        ax.set_xlabel("月")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("最小核心 v4：三情境時間序列（前沿 vs 任務生成的賽跑）", fontsize=13)
    fig.tight_layout()
    out = os.path.join(FIGDIR, "baseline_timeseries.png")
    fig.savefig(out, dpi=120)
    print(f"\n已存圖：{out}")


if __name__ == "__main__":
    main()
