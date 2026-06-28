"""繪圖共用：嘗試套用系統中文字型，找不到就用預設（圖仍可讀）。"""
from __future__ import annotations
import matplotlib
from matplotlib import font_manager


def setup_cjk_font():
    candidates = [
        "Microsoft JhengHei", "Microsoft YaHei", "PingFang TC", "PingFang SC",
        "Noto Sans CJK TC", "Noto Sans CJK SC", "Source Han Sans TC",
        "SimHei", "Heiti TC", "Arial Unicode MS",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            matplotlib.rcParams["font.sans-serif"] = [name]
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name
    matplotlib.rcParams["axes.unicode_minus"] = False
    return None  # 沒有中文字型；標題中文可能顯示為方框，不影響數據
