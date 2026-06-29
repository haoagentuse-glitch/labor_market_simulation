"""
基線與三情境：時間序列圖。
    uv run python scripts/run.py

輸出（results/<版本>/）：
    figures/baseline_timeseries.png   三情境 × 多面板時間序列
    data/baseline_timeseries.csv      每情境每指標的逐月數值（文字版）
    summary.json / manifest.json

四面板含新拆出的「在職者 Gini」，與舊「全體 Gini」對照看就業汙染。
"""

from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")          # 無顯示環境，直接存檔
import matplotlib.pyplot as plt

from labor_sim.model import Params, run_sim
from labor_sim.plotutil import setup_cjk_font
from labor_sim import output

setup_cjk_font()

# 實作後的發現：靜態能力下，前沿 F 掃過固定能力分佈會讓所有低於 F 的人失業，
# 而任務生成 c 只在前沿「之上」加任務（只有高能力者能接），救不了被替代者。
# 真正切換「崩潰 ↔ 重配置」的是「人類適應速度 g（學習）」與前沿速度 r 的賽跑。
SCENARIOS = {
    "崩潰 r≫g (無學習)":  dict(r=0.005, human_learning=0.000),
    "拉鋸 r≈g":          dict(r=0.004, human_learning=0.004),
    "重配置 g≥r":        dict(r=0.003, human_learning=0.006),
}

# 要畫 / 要匯出的指標（attr, 中文標題）
PANELS = [
    ("employment_rate", "就業率 employment"),
    ("human_zone",      "人類保護區寬度 σ_max−F"),
    ("gini",            "全體 Gini（含失業者）"),
    ("gini_employed",   "在職者 Gini（只算 earnings>0）"),
    ("top10_share",     "頂端 10% 收入份額"),
]


def main():
    results = {name: run_sim(Params(**kw)) for name, kw in SCENARIOS.items()}

    # 終端機摘要
    print(f"版本={output.version()}")
    print(f"{'情境':12s} {'regime':14s} {'emp':>5s} {'gini':>5s} {'giniE':>6s} {'top10':>6s} {'zone':>5s}")
    for name, res in results.items():
        print(f"{name:12s} {res.regime:14s} "
              f"{res.employment_rate[-1]:5.2f} {res.gini[-1]:5.2f} "
              f"{res.gini_employed[-1]:6.2f} {res.top10_share[-1]:6.2f} {res.human_zone[-1]:5.2f}")

    # 圖：5 面板（2×3，最後一格留空）× 三情境
    months = np.arange(next(iter(results.values())).employment_rate.size)
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    flat = axes.ravel()
    for ax, (attr, title) in zip(flat, PANELS):
        for name, res in results.items():
            ax.plot(months, getattr(res, attr), label=name, lw=2)
        ax.set_title(title); ax.set_xlabel("月"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    flat[len(PANELS)].axis("off")
    fig.suptitle("最小核心 v4：三情境時間序列（前沿 vs 任務生成的賽跑）", fontsize=13)
    fig.tight_layout()
    fig.savefig(output.fig_path("baseline_timeseries.png"), dpi=120)
    plt.close(fig)

    # 文字版資料：寬表，每情境每指標一欄
    cols = {"month": months}
    for name, res in results.items():
        tag = {"崩潰 r≫g (無學習)": "collapse", "拉鋸 r≈g": "tug",
               "重配置 g≥r": "realloc"}.get(name, name)
        for attr, _ in PANELS:
            cols[f"{tag}__{attr}"] = getattr(res, attr)
    output.save_columns("baseline_timeseries.csv", cols)

    # 純量結論：每情境末段值
    summ = {}
    for name, res in results.items():
        summ[name] = {
            "regime": res.regime,
            "employment_final": float(res.employment_rate[-1]),
            "gini_all_final": float(res.gini[-1]),
            "gini_employed_final": float(res.gini_employed[-1]),
            "top10_final": float(res.top10_share[-1]),
            "human_zone_final": float(res.human_zone[-1]),
        }
    output.update_summary("baseline", summ)

    output.record_manifest("run.py",
                           params={k: dict(v) for k, v in SCENARIOS.items()},
                           seeds=[0],
                           notes="三情境時間序列；含 gini_employed 對照")
    print(f"已存圖：baseline_timeseries.png → {output.results_dir()}")


if __name__ == "__main__":
    main()
