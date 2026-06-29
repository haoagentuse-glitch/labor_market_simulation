"""
相圖（v4 的主要交付物）+ 臨界前沿速度曲線。
    uv run python scripts/sweep.py

輸出（results/<版本>/）：
    figures/phase_macro.png         宏觀賽跑 (r, g) → 末段就業率，疊上 r*(g) 臨界線
    figures/phase_distribution.png  分配結局：top10 份額 vs 在職者 Gini（並列）
    figures/critical_frontier.png   r*(g)：每個學習速度 g 對應的崩潰臨界前沿速度
    data/phase_macro_employment.csv
    data/phase_distribution_top10.csv
    data/phase_distribution_gini_employed.csv
    data/critical_frontier_r_star.csv
    summary.json（各圖純量結論）, manifest.json（參數/種子/git）

本版（B 清單）重點：
  * B-1 拆分配相圖：除了 top10 份額，加「在職者 Gini」(只算 earnings>0)，
    直接驗證/推翻 L_0.1.0「能力越均質越集中」這個疑似就業汙染的反直覺結論。
  * B-3 量化臨界前沿速度 r*(g)：把「前沿有結構性優勢」變成一條可引用的線。

每格多種子平均，降低雜訊。格數可調（GRID）。
"""

from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from labor_sim.model import Params, run_sim
from labor_sim.plotutil import setup_cjk_font
from labor_sim import output

setup_cjk_font()

GRID = 13          # 每軸格數（先小一點求快，要細再加）
SEEDS = 3          # 每格平均的種子數
EMP_CRIT = 0.5     # 崩潰臨界：末段就業率跌破此值視為崩潰，用來定義 r*

# 掃描軸（集中放這裡，匯出 manifest 用）
RS = np.linspace(0.001, 0.007, GRID)      # 前沿上升速度 r
GS = np.linspace(0.000, 0.008, GRID)      # 人類學習速度 g
SIGMAS = np.linspace(0.2, 1.2, GRID)      # 能力尾巴重度 ability_sigma
KS = np.linspace(0.5, 3.0, GRID)          # 價值凸度 k


def _avg(metric_fn, base_kw, seeds=SEEDS):
    vals = [metric_fn(run_sim(Params(seed=s, **base_kw))) for s in range(seeds)]
    return float(np.nanmean(vals))


def _crossing(rs: np.ndarray, emp_row: np.ndarray, crit: float) -> float:
    """
    在固定 g 的這一列上，沿 r 遞增找就業率由上往下穿越 crit 的 r 值（線性內插）。
    emp 隨 r 上升而下降：r 越大越崩潰。
      - 整列都 >= crit（範圍內沒崩潰）→ NaN
      - 整列都 < crit（一開始就崩潰）  → rs[0]
    """
    below = emp_row < crit
    if not below.any():
        return float("nan")
    j = int(np.argmax(below))            # 第一個跌破的索引
    if j == 0:
        return float(rs[0])
    r0, r1 = rs[j - 1], rs[j]
    e0, e1 = emp_row[j - 1], emp_row[j]
    if e0 == e1:
        return float(r1)
    return float(r0 + (crit - e0) * (r1 - r0) / (e1 - e0))


def phase_macro():
    """宏觀賽跑：前沿速度 r vs 人類學習速度 g → 崩潰 / 重配置；附 r*(g) 臨界線。"""
    emp = np.zeros((GRID, GRID))
    for i, g in enumerate(GS):               # 列：g
        for j, r in enumerate(RS):           # 行：r
            emp[i, j] = _avg(lambda R: R.employment_rate[-12:].mean(),
                             dict(r=r, human_learning=g))

    r_star = np.array([_crossing(RS, emp[i], EMP_CRIT) for i in range(GRID)])

    # --- 圖 ---
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(emp, origin="lower", aspect="auto", cmap="RdYlGn",
                   vmin=0, vmax=1, extent=[RS[0], RS[-1], GS[0], GS[-1]])
    lo, hi = max(RS[0], GS[0]), min(RS[-1], GS[-1])
    ax.plot([lo, hi], [lo, hi], "k--", lw=1.2, label="r = g（對角參考線）")
    finite = np.isfinite(r_star)
    ax.plot(r_star[finite], GS[finite], "o-", color="black", lw=1.8, ms=4,
            label=f"r*(g)：崩潰臨界（emp={EMP_CRIT:g}）")
    ax.set_xlabel("前沿上升速度 r")
    ax.set_ylabel("人類學習速度 g")
    ax.set_title("宏觀相圖：末段就業率\n（綠=重配置存活，紅=結構性崩潰）")
    ax.set_xlim(RS[0], RS[-1]); ax.set_ylim(GS[0], GS[-1])
    ax.legend(loc="lower right", fontsize=8)
    fig.colorbar(im, ax=ax, label="末段就業率")
    fig.tight_layout()
    fig.savefig(output.fig_path("phase_macro.png"), dpi=120)
    plt.close(fig)

    # --- r*(g) 單獨一張，凸顯是否接近垂直（前沿結構性優勢）---
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    ax2.plot(GS[finite], r_star[finite], "o-", color="#b2182b", lw=2)
    ax2.set_xlabel("人類學習速度 g")
    ax2.set_ylabel("崩潰臨界前沿速度 r*")
    ax2.set_title("臨界前沿速度 r*(g)\n（近水平=前沿主宰；強上升=學習能救）")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(output.fig_path("critical_frontier.png"), dpi=120)
    plt.close(fig2)

    # --- 文字版資料 ---
    output.save_grid("phase_macro_employment.csv", RS, GS, emp,
                     xlabel="r", ylabel="g", value="employment_final")
    output.save_columns("critical_frontier_r_star.csv",
                        {"g": GS, "r_star": r_star})

    # --- 純量結論 ---
    rs_fit = r_star[finite]
    gs_fit = GS[finite]
    slope = float(np.polyfit(gs_fit, rs_fit, 1)[0]) if rs_fit.size >= 2 else float("nan")
    output.update_summary("phase_macro", {
        "metric": "末段就業率(最後12步均值)",
        "emp_crit_for_r_star": EMP_CRIT,
        "r_star_min": _nanfloat(np.nanmin(r_star)),
        "r_star_max": _nanfloat(np.nanmax(r_star)),
        "r_star_mean": _nanfloat(np.nanmean(r_star)),
        "r_star_vs_g_slope": slope,
        "interpretation": ("slope≈0 → 臨界線近垂直、前沿速度結構性主宰命運；"
                           "slope 越大 → 學習 g 越能把臨界往右推。"),
        "emp_min": float(np.min(emp)),
        "emp_max": float(np.max(emp)),
    })
    print(f"已存圖：phase_macro.png, critical_frontier.png  | r* 斜率≈{slope:.3f}")


def phase_distribution():
    """
    分配：能力尾巴 ability_sigma vs 價值凸度 k。
    並列兩個集中度指標，把「就業水準汙染」拆乾淨：
      左：top10 份額（舊指標，含失業者 0 收入 → 受就業汙染）
      右：在職者 Gini（只算 earnings>0 → 純集中度）  ← B-1 關鍵
    """
    top = np.zeros((GRID, GRID))
    gemp = np.zeros((GRID, GRID))
    for i, k in enumerate(KS):               # 列：k
        for j, sg in enumerate(SIGMAS):      # 行：sigma
            base = dict(ability_sigma=sg, V_curvature=k)
            top[i, j] = _avg(lambda R: R.top10_share[-12:].mean(), base)
            gemp[i, j] = _avg(lambda R: np.nanmean(R.gini_employed[-12:]), base)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    ext = [SIGMAS[0], SIGMAS[-1], KS[0], KS[-1]]

    im0 = axes[0].imshow(top, origin="lower", aspect="auto", cmap="magma",
                         vmin=0.1, vmax=1.0, extent=ext)
    axes[0].set_title("舊指標：頂端 10% 收入份額\n（含失業者 → 受就業水準汙染）")
    axes[0].set_xlabel("能力尾巴重度 ability_sigma"); axes[0].set_ylabel("價值凸度 k")
    fig.colorbar(im0, ax=axes[0], label="top10 份額")

    im1 = axes[1].imshow(gemp, origin="lower", aspect="auto", cmap="viridis",
                         extent=ext)
    axes[1].set_title("乾淨指標：在職者 Gini\n（只算 earnings>0 → 純集中度）")
    axes[1].set_xlabel("能力尾巴重度 ability_sigma"); axes[1].set_ylabel("價值凸度 k")
    fig.colorbar(im1, ax=axes[1], label="在職者 Gini")

    fig.suptitle("分配相圖：集中度指標對照（拆開就業汙染）", fontsize=12)
    fig.tight_layout()
    fig.savefig(output.fig_path("phase_distribution.png"), dpi=120)
    plt.close(fig)

    output.save_grid("phase_distribution_top10.csv", SIGMAS, KS, top,
                     xlabel="ability_sigma", ylabel="k", value="top10_share")
    output.save_grid("phase_distribution_gini_employed.csv", SIGMAS, KS, gemp,
                     xlabel="ability_sigma", ylabel="k", value="gini_employed")

    # 沿 ability_sigma 的單調方向：均質(小sigma)→重尾(大sigma) 時，乾淨集中度是升是降？
    top_trend = float(np.mean(top[:, -1] - top[:, 0]))    # 重尾 - 均質
    gemp_trend = float(np.mean(gemp[:, -1] - gemp[:, 0]))
    output.update_summary("phase_distribution", {
        "metric_old": "頂端10%份額(含失業者)",
        "metric_clean": "在職者Gini(earnings>0)",
        "top10_trend_heavy_minus_homog": top_trend,
        "gini_emp_trend_heavy_minus_homog": gemp_trend,
        "verdict": ("若 gini_emp_trend>0（重尾→更集中），則 L_0.1.0「能力越均質越集中」"
                    "為就業汙染假象，被推翻；若仍≤0，則該反直覺結論在乾淨指標下成立。"),
        "top10_min": float(top.min()), "top10_max": float(top.max()),
        "gini_emp_min": float(gemp.min()), "gini_emp_max": float(gemp.max()),
    })
    print(f"已存圖：phase_distribution.png  | 在職者Gini 重尾-均質趨勢={gemp_trend:+.3f}")


def _nanfloat(x):
    x = float(x)
    return None if np.isnan(x) else x


if __name__ == "__main__":
    print(f"版本={output.version()}  掃描中（GRID={GRID}, SEEDS={SEEDS}）…")
    phase_macro()
    phase_distribution()
    output.record_manifest("sweep.py",
                           params={"GRID": GRID, "SEEDS": SEEDS, "EMP_CRIT": EMP_CRIT},
                           seeds=list(range(SEEDS)),
                           notes="r掃[0.001,0.007] g掃[0,0.008] sigma掃[0.2,1.2] k掃[0.5,3.0]")
    print(f"完成。輸出 → {output.results_dir()}")
