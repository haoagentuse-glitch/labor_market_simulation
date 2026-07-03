# labor-sim — AI 時代勞動市場演化模擬（最小核心 v4）

第一性原理的最小實作：**三個純量 + 一條規則**，讓替代、協作、逃跑賽跑、集中／壓縮全部從規則**浮現**，而非被設定。
完整演進見 `docs/05_evolution.md`；文件地圖與進度見 `docs/00_index.md`；歸檔規則見 `docs/01_sop.md`。

```
task : σ   任務離 AI 前沿多遠（需要多少「賦予結構」的能力）
人   : a   能力，異質分佈（尾巴形狀可掃描）
AI   : F(t) 前沿，隨時間以速度 r 上爬
規則 : σ<F → AI 替代；σ≥F → 需 a≥σ 的人協作，產出 V(σ)=σ^k（排序匹配）
```

## 目錄結構

```
labor_market_simulation/
├── README.md  pyproject.toml  uv.lock  .gitignore
├── src/labor_sim/          核心套件
│   ├── model.py            引擎：三純量一規則、排序匹配、指標、體制分類
│   ├── output.py           版本化輸出：results/<版本>/{figures,data}+summary+manifest
│   └── plotutil.py         中文字型設定
├── scripts/                執行腳本（匯入 labor_sim；輸出到 results/<版本>/）
│   ├── run.py              三情境時間序列（L_0.2.0）
│   ├── sweep.py            相圖 + r*(g) 臨界曲線
│   ├── process.py          過程圖（多種子 + 分位帶）
│   ├── sensitivity.py      ±20% 尺度敏感度
│   └── run_v021.py         L_0.2.1 地基校準基線（槽位校準 + 飽和學習）
├── docs/                   文件（扁平單層，檔名 = 類別碼_類別_定位符，見 docs/01_sop.md）
│   └── 00_index.md         ← 文件地圖與進度，先讀這
├── results/<版本>/         版本化結果（figures 忽略、data/summary/manifest 進版控）
└── _private_notes/         私人筆記（白話解釋、名詞表、CODE_GUIDE）
```

## 快速開始（uv）

```bash
uv sync                                   # 安裝依賴並以 editable 安裝 labor_sim
uv run python -m labor_sim.model          # 冒煙測試：印三情境末段指標
uv run python scripts/run.py              # 三情境時間序列 → results/L_0.2.0/
uv run python scripts/sweep.py            # 相圖 + r*(g)（GRID=13, SEEDS=3）
uv run python scripts/process.py          # 過程圖（16 種子 + 分位帶）
uv run python scripts/sensitivity.py      # 尺度敏感度
uv run python scripts/run_v021.py         # L_0.2.1 地基校準基線 → results/L_0.2.1/
```

> 版本字串由 `src/labor_sim/output.py` 的 `_DEFAULT_VERSION` 或環境變數 `LSIM_VERSION` 決定。
> 每支腳本每產一張圖，同步寫對應 `data/*.csv` 與 `summary.json`，讀結論走文字、不走像素。

## 兩個核心旋鈕（整張相圖的骨幹）

```
宏觀賽跑：  r（前沿速度） vs  g（人類學習速度）   → 崩潰 / 重配置
分配結局：  ability_sigma（能力尾巴） × k（價值凸度） → 集中 / 壓縮
```

## L_0.2.1 地基旋鈕（預設關、向後相容）

- `tasks_per_worker`：校準 t=0 人類任務/工人比，消除「槽位假性失業」（約 25% 的人為地板）。
- `ability_ceiling`：學習改飽和式 `a += g·(ceiling−a)`，取代無上限複利。

## 目前狀態（單一事實來源：docs/00_index.md）

- **v4** 核心穩定；**L_0.2.0** 完成量測校準（推翻「越均質越集中」的量測假象、量化 r\*(g)）。
- **L_0.2.1** 地基校準已執行：槽位校準＋飽和學習後，三情境 regime 完全不變（方向穩健）。
- 概念上正探索 **λ 可表徵性 × ν 回饋密度** 的任務空間（`docs/10_concept_v4_task-ontology.md`，尚未實作）；
  另有終局開放性的候選機制清單（`docs/40_log_20260703_open-endgame-discussion.md`）。

## 備註

- 引擎是純 numpy，單次 240 步模擬約毫秒級。
- 若 `.venv/` 在沙箱建到一半壞掉，刪掉重跑 `uv sync`。
