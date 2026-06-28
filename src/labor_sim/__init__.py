"""labor_sim — AI 時代勞動市場演化模擬：最小核心（三純量 + 一條規則）。"""

from labor_sim.model import (
    Params,
    Result,
    run_sim,
    classify_regime,
    gini,
    top_share,
)

__all__ = [
    "Params",
    "Result",
    "run_sim",
    "classify_regime",
    "gini",
    "top_share",
]

__version__ = "0.1.0"
