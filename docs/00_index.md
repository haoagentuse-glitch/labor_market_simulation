# 00_index — 文件地圖與進度

> 類別:index | 狀態:active | 日期:2026-07-04
> 任何 session 從這裡開始。歸檔與寫作規範見 [01_sop.md](01_sop.md);第一次讀專案看 [05_evolution.md](05_evolution.md)。
> 版號慣例:concept 與 spec 各自獨立計數;spec 沿歷史編號從 v4 起算(v1–v3 是 concept 的加法時代)。

## 1. 文件地圖

| 檔案 | 類別 | 狀態 | 一句話 |
|---|---|---|---|
| [01_sop.md](01_sop.md) | sop | active | 文件規範:命名文法、九類模板、反 slop 硬規則(canonical 在 skill `research-docs`) |
| [05_evolution.md](05_evolution.md) | evolution | active | ★ 一頁總覽:故事版 + 三軌時間線 + 分軌指引 |
| [10_concept_v1.md](10_concept_v1.md) | concept | superseded | 四維職業分類 + ABM 研究框架(起點) |
| [10_concept_v2.md](10_concept_v2.md) | concept | superseded | 去套套邏輯:隨機前沿、擁擠、回饋迴路、體制相圖 |
| [10_concept_v3.md](10_concept_v3.md) | concept | superseded | 雙通道(替代/協作)、推導增益函式、能力重尾分岔 |
| [10_concept_v4_task-ontology.md](10_concept_v4_task-ontology.md) | concept | **active(本體線)** | 任務基元 λ(可表徵)×ν(回饋密度):σ 降為衍生量、前沿律、H1–H3 可證偽 |
| [10_concept_v5_open-endgame.md](10_concept_v5_open-endgame.md) | concept | **active(動力學線)** | 終局開放:F 天花板、labor_share、世代主比值、編碼化對照、歷史校準點;H1–H4 |
| [20_spec_v4.md](20_spec_v4.md) | spec | **active** | 實作真理來源:三純量一規則(v4.1;宏觀賽跑 r vs g) |
| [30_exp_ledger.md](30_exp_ledger.md) | exp | active | 實驗台帳:每版動機/改動/headline/產物 + results 歸檔規範 |
| [30_exp_L0.1.0.md](30_exp_L0.1.0.md) | exp | frozen | 首輪四結論;其中集中度結論後被 L0.2.0 推翻(見檔頭後記) |
| [30_exp_L0.2.0.md](30_exp_L0.2.0.md) | exp | frozen | 量尺校準:在職者 Gini 推翻假象、r\*(g) 斜率 0.425 封頂 ≈0.0043、±20% 零翻面 |
| [30_exp_L0.3.0.md](30_exp_L0.3.0.md) | exp | frozen | F 天花板:終局從 2 種變 3 種(human_premium 浮現)→ H1 成立、單調終局定理推翻;Engels' Pause 脫鉤 14pp |
| [40_log_20260703_open-endgame-discussion.md](40_log_20260703_open-endgame-discussion.md) | log | frozen | 終局開放性:單調終局批判、歷史校準點、螺旋史觀 → 6 項候選機制 |
| [50_sparks.md](50_sparks.md) | sparks | active | 八則轉折:卡在哪→想通了什麼→為什麼關鍵 |
| [90_raw_20260701_gemini-rgb.md](90_raw_20260701_gemini-rgb.md) | raw | frozen | Gemini RGB/HSV 原始提案(真金已入 concept v4) |
| [90_raw_20260701_next-task-brief.md](90_raw_20260701_next-task-brief.md) | raw | frozen | L_0.2.0 起跑簡報(該輪已完成) |
| [90_raw_20260703_spec-v4-draft.md](90_raw_20260703_spec-v4-draft.md) | raw | frozen | spec v4 原稿(含被否證的 r vs c 推導層疊) |
| [90_raw_20260703_task-ontology-draft.md](90_raw_20260703_task-ontology-draft.md) | raw | frozen | 本體論原始思考全文(四方案 + 三輪修訂) |

程式:**`../notebooks/<版號>.ipynb`(L_0.2.2 起,notebook-primary,規範見 01_sop §9)**;`../src/labor_sim/` 與 `../scripts/` 凍結為 legacy(重現 L≤0.2.1)。結果 `../results/<版本>/`、私人筆記 `../_private_notes/`。

## 2. 目前進度(2026-07-04)

- 引擎重構為三實體(`Human`/`Matrix`/`Market`)+ 可插拔機制(`mechanisms/`),L_0.3.0 落地;回歸對 L_0.2.2 **零漂移**(max_rel_drift=0.0)。
- **L_0.3.0(F 天花板)已執行**:加一個天花板參數,終局從 2 種變 3 種(collapse/reallocation/**human_premium**)→ **H1 成立,「單調全面取代」定理被推翻**(`30_exp_L0.3.0`)。H2(Engels' Pause)定性成立(就業 0.97、labor_share 跌 14pp),定量差 1pp 未達 15pp 門檻,列 L_0.3.1 補。
- L_0.1.0→L_0.2.2 歷史:量尺校準(L_0.2.0)、地基校準(L_0.2.1)、notebook-primary 遷移(L_0.2.2),詳見 `30_exp_ledger`。
- 概念線兩軌並行:本體 `10_concept_v4_task-ontology`(λν,未實作)、動力學 `10_concept_v5_open-endgame`(H1 已驗)。
- 規範:文件 `01_sop`/skill `research-docs`;程式碼 notebook-primary + 三實體引擎(§9)。

## 3. 下一步

1. **L_0.3.1 補 H2 定量**(便宜):低 ceiling × 多 g 細掃 labor_share 跌幅找 ≥15pp 格 + human_premium 邊界多種子確認;labor_share 併入標準過程指標圖組。
2. **接第二個機制**(concept v5 §5 序):內生前沿 + 編碼化回饋成對對照(spec §5 待加清單第 2 項)。
3. **λν 最小 2D 原型**(並行本體線):`10_concept_v4` §5 草案,必含各向同性對照。
- 每輪完成 → `30_exp_ledger` 加節 + 獨立 `30_exp_*` 檢討(由淺入深)。
