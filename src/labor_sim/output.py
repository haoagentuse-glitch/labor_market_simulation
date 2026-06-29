"""
輸出 / 版本化層
================
把每次實驗的「圖、文字版資料、純量結論、執行清單」寫進一個**版本化、永不覆蓋**的
資料夾 ``results/<版本>/``，讓每一輪迭代都留下可對照、可重現、可被機器（與 Claude）
直接閱讀的紀錄。

設計原則
--------
* **不覆蓋**：版本（如 ``L_0.2.0``）一個資料夾，跑新版本就換資料夾。
* **圖必有對應文字檔**：每張圖旁邊都寫一份 CSV（畫圖用的陣列）+ 一行 summary.json
  （那張圖的純量結論），之後讀結論不必看圖。
* **可重現**：manifest.json 記錄 git hash、時間、每支腳本用的參數與種子。
* **單一版本來源**：版本字串只在這裡（或環境變數 ``LSIM_VERSION``）決定一次。

資料夾長相::

    results/<版本>/
    ├── figures/    *.png        （git 忽略，可重生）
    ├── data/       *.csv        （進版控）
    ├── summary.json             （純量結論，進版控）
    └── manifest.json            （參數/種子/git/時間，進版控）

格式選擇：CSV + JSON。資料量小（240 步、13×13 格），CSV/JSON 可被直接讀取、可
git diff；不用 Parquet 以免逼出一次 pandas 來回而毫無體積好處。
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import time
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, Sequence

import numpy as np

# 預設版本：每開一輪新迭代就把這裡往上滾，或用環境變數 LSIM_VERSION 覆蓋。
_DEFAULT_VERSION = "L_0.2.0"

# repo 根：src/labor_sim/output.py → 上三層
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --------------------------------------------------------------------------- #
# 版本與路徑
# --------------------------------------------------------------------------- #
def version() -> str:
    """本次輸出的版本字串。可用環境變數 LSIM_VERSION 覆蓋。"""
    return os.environ.get("LSIM_VERSION", _DEFAULT_VERSION).strip()


def results_dir(v: str | None = None) -> str:
    d = os.path.join(ROOT, "results", v or version())
    os.makedirs(d, exist_ok=True)
    return d


def fig_dir(v: str | None = None) -> str:
    d = os.path.join(results_dir(v), "figures")
    os.makedirs(d, exist_ok=True)
    return d


def data_dir(v: str | None = None) -> str:
    d = os.path.join(results_dir(v), "data")
    os.makedirs(d, exist_ok=True)
    return d


def fig_path(name: str, v: str | None = None) -> str:
    """一張圖的完整路徑（會建好資料夾）。傳入檔名如 'phase_macro.png'。"""
    return os.path.join(fig_dir(v), name)


def data_path(name: str, v: str | None = None) -> str:
    return os.path.join(data_dir(v), name)


# --------------------------------------------------------------------------- #
# 寫 CSV
# --------------------------------------------------------------------------- #
def save_columns(name: str, columns: Mapping[str, Sequence[float]],
                 v: str | None = None) -> str:
    """
    寫「等長欄位」CSV（每欄一條曲線 / 一個指標）。
    name 例：'baseline_timeseries.csv'；columns 例：{'month': [...], 'emp': [...]}。
    回傳寫出的路徑。
    """
    keys = list(columns.keys())
    cols = [np.asarray(columns[k]).ravel() for k in keys]
    n = max((c.size for c in cols), default=0)
    # 對齊長度（多種子分位等理應同長；保險起見補 NaN）
    cols = [_pad(c, n) for c in cols]
    path = data_path(name, v)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(keys)
        for i in range(n):
            w.writerow([_fmt(c[i]) for c in cols])
    return path


def save_grid(name: str, x: Sequence[float], y: Sequence[float],
              Z: np.ndarray, xlabel: str = "x", ylabel: str = "y",
              value: str = "value", v: str | None = None) -> str:
    """
    寫相圖網格為 long-form CSV：每列 (xlabel, ylabel, value)。
    Z 形狀 (len(y), len(x))，Z[i, j] 對應 (x[j], y[i])，與 imshow origin='lower' 一致。
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    Z = np.asarray(Z, float)
    path = data_path(name, v)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([xlabel, ylabel, value])
        for i in range(y.size):
            for j in range(x.size):
                w.writerow([_fmt(x[j]), _fmt(y[i]), _fmt(Z[i, j])])
    return path


# --------------------------------------------------------------------------- #
# summary.json（純量結論，逐次合併）
# --------------------------------------------------------------------------- #
def update_summary(section: str, payload: Mapping[str, Any],
                   v: str | None = None) -> str:
    """把一個 section 的純量結論併入 results/<ver>/summary.json。"""
    path = os.path.join(results_dir(v), "summary.json")
    data = _load_json(path)
    data.setdefault("_version", v or version())
    data[section] = _jsonable(payload)
    _dump_json(path, data)
    return path


# --------------------------------------------------------------------------- #
# manifest.json（可重現性：參數 / 種子 / git / 時間）
# --------------------------------------------------------------------------- #
def record_manifest(script: str, params: Any = None, seeds: Any = None,
                    notes: str | None = None, v: str | None = None,
                    **extra: Any) -> str:
    """記錄一支腳本這次跑的設定，併入 results/<ver>/manifest.json[script]。"""
    path = os.path.join(results_dir(v), "manifest.json")
    data = _load_json(path)
    data.setdefault("_version", v or version())
    data.setdefault("_git_hash", git_hash())
    data["_updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry: dict[str, Any] = {
        "ran_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "params": _params_dict(params),
    }
    if seeds is not None:
        entry["seeds"] = _jsonable(seeds)
    if notes:
        entry["notes"] = notes
    entry.update(_jsonable(extra))
    data.setdefault("scripts", {})[script] = entry
    _dump_json(path, data)
    return path


def git_hash() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# 小工具
# --------------------------------------------------------------------------- #
def _pad(a: np.ndarray, n: int) -> np.ndarray:
    if a.size == n:
        return a
    out = np.full(n, np.nan)
    out[: a.size] = a[:n]
    return out


def _fmt(x: Any) -> Any:
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return x
    if np.isnan(xf):
        return ""
    return f"{xf:.6g}"


def _params_dict(params: Any) -> Any:
    if params is None:
        return None
    if is_dataclass(params) and not isinstance(params, type):
        return _jsonable(asdict(params))
    if isinstance(params, Mapping):
        return _jsonable(dict(params))
    return _jsonable(params)


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, Mapping):
        return {str(k): _jsonable(val) for k, val in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, np.ndarray):
        return [_jsonable(x) for x in obj.tolist()]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, float) and np.isnan(obj):
        return None
    return obj


def _load_json(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _dump_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
