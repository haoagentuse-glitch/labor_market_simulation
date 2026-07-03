# 00_index — 文件地圖與進度

> 類別:index | 狀態:active | 日期:2026-07-03
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
| [10_concept_v4_task-ontology.md](10_concept_v4_task-ontology.md) | concept | **active** | 任務基元 λ(可表徵)×ν(回饋密度):σ 降為衍生量、前沿律、H1–H3 可證偽 |
| [20_spec_v4.md](20_spec_v4.md) | spec | **active** | 實作真理來源:三純量一規則(v4.1;宏觀賽跑 r vs g) |
| [30_exp_ledger.md](30_exp_ledger.md) | exp | active | 實驗台帳:每版動機/改動/headline/產物 + results 歸檔規範 |
| [30_exp_L0.1.0.md](30_exp_L0.1.0.md) | exp | frozen | 首輪四結論;其中集中度結論後被 L0.2.0 推翻(見檔頭後記) |
| [30_exp_L0.2.0.md](30_exp_L0.2.0.md) | exp | frozen | 量尺校準:在職者 Gini 推翻假象、r\*(g) 斜率 0.425 封頂 ≈0.0043、±20% 零翻面 |
| [40_log_20260703_open-endgame-discussion.md](40_log_20260703_open-endgame-discussion.md) | log | frozen | 終局開放性:單調終局批判、歷史校準點、螺旋史觀 → 6 項候選機制 |
| [50_sparks.md](50_sparks.md) | sparks | active | 八則轉折:卡在哪→想通了什麼→為什麼關鍵 |
| [90_raw_20260701_gemini-rgb.md](90_raw_20260701_gemini-rgb.md) | raw | frozen | Gemini RGB/HSV 原始提案(真金已入 concept v4) |
| [90_raw_20260701_next-task-brief.md](90_raw_20260701_next-task-brief.md) | raw | frozen | L_0.2.0 起跑簡報(該輪已完成) |
| [90_raw_20260703_spec-v4-draft.md](90_raw_20260703_spec-v4-draft.md) | raw | frozen | spec v4 原稿(含被否證的 r vs c 推導層疊) |
| [90_raw_20260703_task-ontology-draft.md](90_raw_20260703_task-ontology-draft.md) | raw | frozen | 本體論原始思考全文(四方案 + 三輪修訂) |

程式 `../src/labor_sim/`(引擎 `model.py`)、腳本 `../scripts/`、結果 `../results/<版本>/`、私人筆記 `../_private_notes/`。

## 2. 目前進度(2026-07-03)

- v4.1 核心穩定(σ/a/F + 排序匹配 + g + retrain_rate);L_0.1.0 四結論經 L_0.2.0 校準:1 推翻、1 修正、2 強化(`30_exp_ledger`)。
- L_0.2.1 地基校準已執行:三情境 regime 完全不變、t=0 失業 0.254→0.160、在職者 Gini 排序不變(`results/L_0.2.1/summary.json`);待補 `ability_ceiling` 敏感度。
- 概念線:λν 本體整併為 `10_concept_v4_task-ontology`(active,未實作),原稿入 raw。
- 終局開放討論凍結於 `40_log_20260703`,6 項候選機制【待決】。
- docs 全面依 `01_sop` 標準化(2026-07-03):扁平命名、檔頭狀態列、模板對齊;規範升級為個人層 skill `research-docs`。

## 3. 下一步

1. **補 `ability_ceiling` 敏感度**(L_0.2.1 遺留;更低天花板可能讓重配置臨界前移)——最便宜,先做。
2. **分岔擇一**:(a) λν 最小 2D 原型(`10_concept_v4` §5 草案,必含各向同性對照 H2);(b) F 天花板單參數(`40_log_20260703` §5 機制 1,直接檢驗終局是否仍單調)。兩者一為本體、一為動力學,依「一次一個」憲法分開跑,先後皆可。
3. 跑完任一項 → `30_exp_ledger` 加節 + 獨立 `30_exp_*` 檢討(嚴格由淺入深)。
