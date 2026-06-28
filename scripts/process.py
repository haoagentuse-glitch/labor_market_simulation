"""
過程／機制圖（解釋因果，不只結果指標）。
    uv run python scripts/process.py
輸出：
    figures/occupation_structure.png  職業結構變化（層級人口比例、AI 替代率、新職業生成率）
    figures/skill_evolution.png       技能演化（平均技能、再訓練成功率、需求 vs 供給落差）

用一個「拉鋸」情境（前沿與學習相當、含再訓練），讓過程動態最豐富。
"""

from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from labor_sim.model import Params, run_sim, OCC_LABELS
from labor_sim.plotutil import setup_cjk_font

setup_cjk_font()

FIGDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIGDIR, exist_ok=True)

# 代表性情境：前沿 r 與學習 g 相當，並開啟失業者再訓練 → 過程最有看頭
SCENARIO = dict(r=0.004, human_learning=0.004, retrain_rate=0.002, seed=0)


def _smooth(x, w=6):
    """簡單移動平均，讓逐步雜訊的曲線（如再訓練成功率）好讀。"""
    x = np.asarray(x, float)
    if w <= 1:
        return x
    kernel = np.ones(w) / w
    return np.convolve(x, kernel, mode="same")


def fig_occupation(res):
    months = np.arange(res.employment_rate.size)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # (A) 各職業層級人口比例（堆疊面積）
    ax = axes[0]
    colors = ["#bdbdbd", "#4575b4", "#91bfdb", "#fc8d59", "#d73027"]
    ax.stackplot(months, *[res.occ_shares[:, i] for i in range(5)],
                 labels=OCC_LABELS, colors=colors, alpha=0.9)
    ax.set_title("職業結構變化：各層級人口比例")
    ax.set_xlabel("月"); ax.set_ylabel("人口比例")
    ax.set_xlim(0, months[-1]); ax.set_ylim(0, 1)
    ax.legend(loc="upper left", fontsize=8, ncol=2)

    # (B) AI 替代率 與 新職業生成率
    ax = axes[1]
    ax.plot(months, res.ai_substitution, color="#d73027", lw=2, label="AI 替代率（任務價值佔比）")
    ax.plot(months, res.new_job_rate, color="#1a9850", lw=2, label="新職業生成率（σ>σ_max0 價值佔比）")
    ax.set_title("替代 vs 生成：兩股力量的賽跑")
    ax.set_xlabel("月"); ax.set_ylabel("佔比")
    ax.set_xlim(0, months[-1]); ax.set_ylim(0, 1)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    fig.suptitle(f"圖一　職業結構變化　scenario={SCENARIO}", fontsize=12)
    fig.tight_layout()
    out = os.path.join(FIGDIR, "occupation_structure.png")
    fig.savefig(out, dpi=120)
    print(f"已存圖：{out}")


def fig_skill(res):
    months = np.arange(res.employment_rate.size)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # (A) 平均技能值
    ax = axes[0, 0]
    ax.plot(months, res.mean_ability, lw=2, label="全體平均技能 a")
    ax.plot(months, res.mean_ability_emp, lw=2, label="在崗者平均技能 a")
    ax.plot(months, res.F, "k--", lw=1.2, label="AI 前沿 F")
    ax.set_title("平均技能值演化")
    ax.set_xlabel("月"); ax.set_ylabel("技能 / 前沿")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    # (B) 再訓練成功率
    ax = axes[0, 1]
    ax.plot(months, _smooth(res.retrain_success), color="#2c7fb8", lw=2)
    ax.set_title("再訓練成功率（上步失業→本步就業，6 月平滑）")
    ax.set_xlabel("月"); ax.set_ylabel("成功率")
    ax.set_ylim(0, max(0.05, np.nanmax(res.retrain_success) * 1.1))
    ax.grid(alpha=0.3)

    # (C) 技能需求 vs 供給（落差 = 兩線之間）
    ax = axes[1, 0]
    ax.plot(months, res.demand_median, color="#d73027", lw=2, label="技能需求（人類任務 σ 中位）")
    ax.plot(months, res.supply_median, color="#1a9850", lw=2, label="技能供給（worker a 中位）")
    ax.fill_between(months, res.supply_median, res.demand_median,
                    where=(res.demand_median >= res.supply_median),
                    color="#fdae61", alpha=0.4, label="落差（需求>供給）")
    ax.set_title("技能需求與供給的落差")
    ax.set_xlabel("月"); ax.set_ylabel("σ / a")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    # (D) 落差的兩種面向：未填補需求 與 閒置人力
    ax = axes[1, 1]
    ax.plot(months, res.unmet_demand, color="#d73027", lw=2, label="未填補的人類任務（需求端缺口）")
    ax.plot(months, res.unused_supply, color="#7570b3", lw=2, label="閒置人力／失業（供給端缺口）")
    ax.set_title("錯配的兩端")
    ax.set_xlabel("月"); ax.set_ylabel("比例")
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    fig.suptitle(f"圖二　技能演化曲線　scenario={SCENARIO}", fontsize=12)
    fig.tight_layout()
    out = os.path.join(FIGDIR, "skill_evolution.png")
    fig.savefig(out, dpi=120)
    print(f"已存圖：{out}")


def main():
    res = run_sim(Params(**SCENARIO))
    print(f"scenario regime = {res.regime}")
    fig_occupation(res)
    fig_skill(res)


if __name__ == "__main__":
    main()
