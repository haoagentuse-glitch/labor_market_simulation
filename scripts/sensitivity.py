"""
最小穩健性 / 敏感度檢查（B-4，可選）。
    uv run python scripts/sensitivity.py

對核心**尺度參數**各 ±20%，確認結論方向不變（不是被某個尺度校準硬撐出來的）：
    F0              初始前沿
    ability_median  能力分佈中位錨點
    task_density    任務密度

對三個代表情境（崩潰 / 拉鋸 / 重配置）各跑一遍，輸出：
    data/sensitivity.csv   每組 (情境, 參數, 倍率) 的 regime 與末段就業率/在職者Gini
    summary.json           方向是否穩健的判讀

判讀：若同一情境在 ±20% 下 regime 不翻面、emp 變化溫和 → 結論對尺度穩健。
"""

from __future__ import annotations
import collections
import numpy as np

from labor_sim.model import Params, run_sim
from labor_sim import output

SCENARIOS = {
    "collapse": dict(r=0.005, human_learning=0.000),
    "tug":      dict(r=0.004, human_learning=0.004),
    "realloc":  dict(r=0.003, human_learning=0.006),
}
BASE = dict(F0=0.20, ability_median=0.5, task_density=2000.0)
FACTORS = [0.8, 1.0, 1.2]          # ±20% 與基準
SEEDS = 5


def _eval(base_kw):
    emp, gini_e, regimes = [], [], []
    for s in range(SEEDS):
        res = run_sim(Params(seed=s, **base_kw))
        emp.append(res.employment_rate[-12:].mean())
        gini_e.append(np.nanmean(res.gini_employed[-12:]))
        regimes.append(res.regime)
    modal = collections.Counter(regimes).most_common(1)[0][0]
    return float(np.mean(emp)), float(np.nanmean(gini_e)), modal


def main():
    rows = {"scenario": [], "param": [], "factor": [], "value": [],
            "regime": [], "emp_final": [], "gini_emp_final": []}
    flips = []

    for sname, skw in SCENARIOS.items():
        # 基準（factor=1）regime，用來判斷是否翻面
        base_emp, base_ge, base_regime = _eval({**skw, **BASE})
        for param, base_val in BASE.items():
            for f in FACTORS:
                kw = {**skw, **BASE, param: base_val * f}
                emp, ge, regime = _eval(kw)
                rows["scenario"].append(sname)
                rows["param"].append(param)
                rows["factor"].append(f)
                rows["value"].append(base_val * f)
                rows["regime"].append(regime)
                rows["emp_final"].append(emp)
                rows["gini_emp_final"].append(ge)
                if f != 1.0 and regime != base_regime:
                    flips.append(f"{sname}/{param}×{f}: {base_regime}→{regime}")

    # CSV（混型欄位，直接用 csv 寫，不走數值格式化）
    import csv as _csv
    path = output.data_path("sensitivity.csv")
    keys = list(rows.keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = _csv.writer(fh)
        w.writerow(keys)
        for i in range(len(rows["scenario"])):
            w.writerow([rows[k][i] for k in keys])

    output.update_summary("sensitivity", {
        "params_varied": list(BASE.keys()),
        "factors": FACTORS,
        "seeds": SEEDS,
        "regime_flips_under_pm20pct": flips,
        "verdict": ("無翻面 → 三情境結論對尺度校準穩健；"
                    "有翻面 → 該結論靠近相界、對尺度敏感，需標註。"),
    })
    output.record_manifest("sensitivity.py",
                           params={"SCENARIOS": SCENARIOS, "BASE": BASE, "FACTORS": FACTORS},
                           seeds=list(range(SEEDS)),
                           notes="±20% 尺度敏感度")
    print(f"版本={output.version()}  翻面數={len(flips)}  {flips if flips else '（無翻面）'}")
    print(f"已存：data/sensitivity.csv → {output.results_dir()}")


if __name__ == "__main__":
    main()
