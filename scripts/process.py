"""
過程／機制圖（解釋因果，不只結果指標）—— 多種子版。
    uv run python scripts/process.py

輸出（results/<版本>/）：
    figures/occupation_structure.png  職業結構（層級人口比例、AI 替代率、新職業生成率）
    figures/skill_evolution.png       技能演化（平均技能、再訓練、需求 vs 供給落差）
    data/process_occupation.csv       上述曲線的中位數 + 10/90 分位帶
    data/process_skill.csv
    summary.json / manifest.json

本版（B-2）重點：改成跑 N 個 seed，畫中位數 + 10/90 分位帶，
確認「掏空 / 升級 / 錯配」是穩健現象、不是單一 seed 的特例。
"""

from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from labor_sim.model import Params, run_sim, OCC_LABELS
from labor_sim.plotutil import setup_cjk_font
from labor_sim import output

setup_cjk_font()

# 代表性情境：前沿 r 與學習 g 相當，並開啟失業者再訓練 → 過程最有看頭
SCENARIO = dict(r=0.004, human_learning=0.004, retrain_rate=0.002)
SEEDS = 16                         # B-2：多種子，畫中位數 + 分位帶
QLO, QHI = 10, 90                  # 分位帶


def _smooth(x, w=6):
    x = np.asarray(x, float)
    if w <= 1:
        return x
    return np.convolve(x, np.ones(w) / w, mode="same")


def _band(stack: np.ndarray):
    """stack 形狀 (n_seeds, steps) → (median, q_lo, q_hi)，nan 安全。"""
    med = np.nanmedian(stack, axis=0)
    lo = np.nanpercentile(stack, QLO, axis=0)
    hi = np.nanpercentile(stack, QHI, axis=0)
    return med, lo, hi


def run_seeds():
    """跑 SEEDS 個種子，回傳各曲線的 (n_seeds, steps) 堆疊。"""
    attrs = ["occ_shares", "ai_substitution", "new_job_rate", "F",
             "mean_ability", "mean_ability_emp", "retrain_success",
             "demand_median", "supply_median", "unmet_demand", "unused_supply"]
    runs = [run_sim(Params(seed=s, **SCENARIO)) for s in range(SEEDS)]
    out = {}
    for a in attrs:
        out[a] = np.stack([getattr(r, a) for r in runs], axis=0)
    out["_regimes"] = [r.regime for r in runs]
    out["steps"] = runs[0].employment_rate.size
    return out


def fig_occupation(D, months):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # (A) 各職業層級人口比例（堆疊面積，用各 seed 中位數）
    ax = axes[0]
    occ_med = np.nanmedian(D["occ_shares"], axis=0)        # (steps, 5)
    colors = ["#bdbdbd", "#4575b4", "#91bfdb", "#fc8d59", "#d73027"]
    ax.stackplot(months, *[occ_med[:, i] for i in range(5)],
                 labels=OCC_LABELS, colors=colors, alpha=0.9)
    ax.set_title(f"職業結構變化：各層級人口比例（{SEEDS} seed 中位數）")
    ax.set_xlabel("月"); ax.set_ylabel("人口比例")
    ax.set_xlim(0, months[-1]); ax.set_ylim(0, 1)
    ax.legend(loc="upper left", fontsize=8, ncol=2)

    # (B) AI 替代率 與 新職業生成率（中位數 + 分位帶）
    ax = axes[1]
    for key, color, label in [
        ("ai_substitution", "#d73027", "AI 替代率（任務價值佔比）"),
        ("new_job_rate", "#1a9850", "新職業生成率（σ>σ_max0 價值佔比）"),
    ]:
        med, lo, hi = _band(D[key])
        ax.plot(months, med, color=color, lw=2, label=label)
        ax.fill_between(months, lo, hi, color=color, alpha=0.18)
    ax.set_title("替代 vs 生成：兩股力量的賽跑（帶=10–90 分位）")
    ax.set_xlabel("月"); ax.set_ylabel("佔比")
    ax.set_xlim(0, months[-1]); ax.set_ylim(0, 1)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    fig.suptitle(f"圖一　職業結構變化　scenario={SCENARIO}　seeds={SEEDS}", fontsize=12)
    fig.tight_layout()
    fig.savefig(output.fig_path("occupation_structure.png"), dpi=120)
    plt.close(fig)


def fig_skill(D, months):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # (A) 平均技能值
    ax = axes[0, 0]
    for key, label in [("mean_ability", "全體平均技能 a"),
                       ("mean_ability_emp", "在崗者平均技能 a")]:
        med, lo, hi = _band(D[key])
        ax.plot(months, med, lw=2, label=label)
        ax.fill_between(months, lo, hi, alpha=0.18)
    ax.plot(months, np.nanmedian(D["F"], axis=0), "k--", lw=1.2, label="AI 前沿 F")
    ax.set_title("平均技能值演化")
    ax.set_xlabel("月"); ax.set_ylabel("技能 / 前沿")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    # (B) 再訓練成功率
    ax = axes[0, 1]
    rs_stack = np.stack([_smooth(row) for row in D["retrain_success"]], axis=0)
    med, lo, hi = _band(rs_stack)
    ax.plot(months, med, color="#2c7fb8", lw=2)
    ax.fill_between(months, lo, hi, color="#2c7fb8", alpha=0.18)
    ax.set_title("再訓練成功率（上步失業→本步就業，6 月平滑）")
    ax.set_xlabel("月"); ax.set_ylabel("成功率")
    ax.set_ylim(0, max(0.05, float(np.nanmax(hi)) * 1.1))
    ax.grid(alpha=0.3)

    # (C) 技能需求 vs 供給
    ax = axes[1, 0]
    dem_med = np.nanmedian(D["demand_median"], axis=0)
    sup_med = np.nanmedian(D["supply_median"], axis=0)
    ax.plot(months, dem_med, color="#d73027", lw=2, label="技能需求（人類任務 σ 中位）")
    ax.plot(months, sup_med, color="#1a9850", lw=2, label="技能供給（worker a 中位）")
    ax.fill_between(months, sup_med, dem_med, where=(dem_med >= sup_med),
                    color="#fdae61", alpha=0.4, label="落差（需求>供給）")
    ax.set_title("技能需求與供給的落差（中位數）")
    ax.set_xlabel("月"); ax.set_ylabel("σ / a")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    # (D) 錯配兩端
    ax = axes[1, 1]
    for key, color, label in [
        ("unmet_demand", "#d73027", "未填補的人類任務（需求端缺口）"),
        ("unused_supply", "#7570b3", "閒置人力／失業（供給端缺口）"),
    ]:
        med, lo, hi = _band(D[key])
        ax.plot(months, med, color=color, lw=2, label=label)
        ax.fill_between(months, lo, hi, color=color, alpha=0.18)
    ax.set_title("錯配的兩端（帶=10–90 分位）")
    ax.set_xlabel("月"); ax.set_ylabel("比例")
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    fig.suptitle(f"圖二　技能演化曲線　scenario={SCENARIO}　seeds={SEEDS}", fontsize=12)
    fig.tight_layout()
    fig.savefig(output.fig_path("skill_evolution.png"), dpi=120)
    plt.close(fig)


def export(D, months):
    cols = {"month": months}
    occ_med = np.nanmedian(D["occ_shares"], axis=0)
    for i, lab in enumerate(["unemp", "low", "mid", "high", "elite"]):
        cols[f"occ_{lab}_med"] = occ_med[:, i]
    for key, short in [("ai_substitution", "ai_sub"), ("new_job_rate", "newjob")]:
        med, lo, hi = _band(D[key])
        cols[f"{short}_med"], cols[f"{short}_lo"], cols[f"{short}_hi"] = med, lo, hi
    output.save_columns("process_occupation.csv", cols)

    cols2 = {"month": months, "F_med": np.nanmedian(D["F"], axis=0)}
    for key, short in [("mean_ability", "mean_a"), ("mean_ability_emp", "mean_a_emp"),
                       ("retrain_success", "retrain"), ("demand_median", "demand"),
                       ("supply_median", "supply"), ("unmet_demand", "unmet"),
                       ("unused_supply", "unused")]:
        med, lo, hi = _band(D[key])
        cols2[f"{short}_med"], cols2[f"{short}_lo"], cols2[f"{short}_hi"] = med, lo, hi
    output.save_columns("process_skill.csv", cols2)

    def last12(key, fn=np.nanmedian):
        return float(fn(D[key][:, -12:]))
    output.update_summary("process", {
        "seeds": SEEDS,
        "regimes": D["_regimes"],
        "ai_substitution_final": last12("ai_substitution"),
        "new_job_rate_final": last12("new_job_rate"),
        "unemployment_final": last12("unused_supply"),
        "unmet_demand_final": last12("unmet_demand"),
        "demand_median_final": last12("demand_median"),
        "supply_median_final": last12("supply_median"),
        "hollowing_check": "看 process_occupation.csv 的 occ_mid_med 末段相對初期是否下降",
        "robust_note": "分位帶窄 → 現象非單一 seed 特例。",
    })


def main():
    D = run_seeds()
    months = np.arange(D["steps"])
    print(f"版本={output.version()}  scenario={SCENARIO}  seeds={SEEDS}")
    print(f"regimes: {D['_regimes']}")
    fig_occupation(D, months)
    fig_skill(D, months)
    export(D, months)
    output.record_manifest("process.py", params=dict(SCENARIO),
                           seeds=list(range(SEEDS)),
                           notes=f"多種子過程診斷；分位帶 {QLO}-{QHI}")
    print(f"已存圖：occupation_structure.png, skill_evolution.png → {output.results_dir()}")


if __name__ == "__main__":
    main()
