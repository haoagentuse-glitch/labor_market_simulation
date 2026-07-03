"""
L_0.2.1 地基校準基線：槽位校準 + 飽和學習。
    uv run python scripts/run_v021.py

補掉 L_0.2.0 的兩個地基問題（見 docs/30_exp_L0.2.0.md §六）：
  1. 槽位假性失業：t=0 就有 ~25% 失業，其實是「人類任務數 < 工人數」的人為地板，與 AI 無關。
     → tasks_per_worker=1.0 使 t=0 人類任務數 = 工人數，讓失業「只由 AI 造成」。
  2. 指數學習：舊 a*(1+g) 讓在崗者能力 20 年 ×2.6–4.2 倍（無上限複利，不現實）。
     → ability_ceiling 改飽和式 a += g·(ceiling−a)，趨近天花板、永不超過。

輸出 → results/L_0.2.1/。與 L_0.2.0 對照，看校準後結論方向是否不變（穩健性）。
本檔只印 + 存圖/資料，實驗由你執行。
"""

from __future__ import annotations
import os
os.environ.setdefault("LSIM_VERSION", "L_0.2.1")   # 寫進 results/L_0.2.1

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from labor_sim.model import Params, run_sim
from labor_sim.plotutil import setup_cjk_font
from labor_sim import output

setup_cjk_font()

# 地基校準旋鈕（L_0.2.1 的主角）
CALIB = dict(tasks_per_worker=1.0, ability_ceiling=3.0)

SCENARIOS = {
    "崩潰 r≫g (無學習)":  dict(r=0.005, human_learning=0.000),
    "拉鋸 r≈g":          dict(r=0.004, human_learning=0.004),
    "重配置 g≥r":        dict(r=0.003, human_learning=0.006),
}

PANELS = [
    ("employment_rate", "就業率 employment"),
    ("human_zone",      "人類保護區寬度 σ_max−F"),
    ("gini",            "全體 Gini（含失業者）"),
    ("gini_employed",   "在職者 Gini（只算 earnings>0）"),
    ("top10_share",     "頂端 10% 收入份額"),
]


def main():
    print(f"版本={output.version()}  校準={CALIB}")
    # 對照：舊(未校準) vs 新(校準) 的 t=0 與末段就業率
    print(f"{'情境':12s} {'t0_old':>7s} {'t0_new':>7s} {'end_old':>8s} {'end_new':>8s} {'regime_new':>12s}")
    results = {}
    for name, kw in SCENARIOS.items():
        old = run_sim(Params(**kw))                       # 舊行為（未校準）
        new = run_sim(Params(**kw, **CALIB))              # L_0.2.1 校準
        results[name] = new
        print(f"{name:12s} {1-old.employment_rate[0]:7.2f} {1-new.employment_rate[0]:7.2f} "
              f"{old.employment_rate[-1]:8.2f} {new.employment_rate[-1]:8.2f} {new.regime:>12s}")

    months = np.arange(next(iter(results.values())).employment_rate.size)
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    flat = axes.ravel()
    for ax, (attr, title) in zip(flat, PANELS):
        for name, res in results.items():
            ax.plot(months, getattr(res, attr), label=name, lw=2)
        ax.set_title(title); ax.set_xlabel("月"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    flat[len(PANELS)].axis("off")
    fig.suptitle(f"L_0.2.1 校準基線（tasks_per_worker=1.0, ability_ceiling=3.0）", fontsize=13)
    fig.tight_layout()
    fig.savefig(output.fig_path("baseline_v021.png"), dpi=120)
    plt.close(fig)

    cols = {"month": months}
    summ = {}
    for name, res in results.items():
        tag = {"崩潰 r≫g (無學習)": "collapse", "拉鋸 r≈g": "tug", "重配置 g≥r": "realloc"}.get(name, name)
        for attr, _ in PANELS:
            cols[f"{tag}__{attr}"] = getattr(res, attr)
        summ[name] = {
            "regime": res.regime,
            "employment_t0": float(res.employment_rate[0]),
            "employment_final": float(res.employment_rate[-1]),
            "gini_all_final": float(res.gini[-1]),
            "gini_employed_final": float(res.gini_employed[-1]),
            "top10_final": float(res.top10_share[-1]),
        }
    output.save_columns("baseline_v021.csv", cols)
    output.update_summary("baseline_v021", summ)
    output.record_manifest("run_v021.py",
                           params={"CALIB": CALIB, "SCENARIOS": {k: dict(v) for k, v in SCENARIOS.items()}},
                           seeds=[0],
                           notes="L_0.2.1 地基校準：槽位校準(t0充分就業)+飽和學習；與 L_0.2.0 對照穩健性")
    print(f"已存圖：baseline_v021.png → {output.results_dir()}")


if __name__ == "__main__":
    main()
