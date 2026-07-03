# AI 時代勞動市場演化模擬：研究框架與設計文件 v2

> 類別:concept(v2) | 狀態:superseded(由 10_concept_v3 取代) | 日期:2026-06
> 修訂自 v1（2026-06）。本版的核心目標：**把一台「會把假設原樣吐出來的機器」，改造成一個會產生湧現（emergence）的交互系統。**
>
> v1 的文獻底子與四維分類框架是 A 級，原封保留。被重寫的是模擬引擎本身——因為 v1 的計分函數把結論寫進了前提。
>
> 版本日期：2026-06

---

## 0. 為什麼要有 v2：v1 的根本問題

v1 在三個地方把答案寫死，導致第六節的「預期社會現象」其實是方程式的代數重述，而非模擬跑出來的結論：

| v1 的寫死之處 | 為什麼是問題 |
|---|---|
| `substitutability = digitizability × (1 - contextual_embeddedness)` | 替代性是輸入，不是浮現。模型沒有能力推翻它 |
| `human_advantage += structuring_scarcity × (1 - ai_maturity)` | 「結構化稀缺性值錢」是假設，第六節卻當成發現 |
| AI maturity 是外生 S 曲線 | 「人類永遠在逃」的勝負，完全由你設的兩條曲線速度決定，是機械的 |

**ABM 的鐵律**：如果結論能用紙筆從方程式推出來，它就不是好的 ABM 問題。湧現只能來自**交互作用與回饋迴路**，不能來自單一 agent 的計分函數。

v2 的全部改動，都圍繞一件事：**讓 outcome 變成你事先算不出來的東西。**

---

## 一、研究定位（重寫核心提問）

### v1 的提問與它的兩個毛病

> （v1）當 AI 能力持續提升、成本持續下降，人類勞動市場會如何重組——以及什麼特質讓人在這個過程中存活？

- **毛病一（套套邏輯）**：「什麼特質存活」的答案被寫進計分函數，模型只是驗證自己。
- **毛病二（零和框架）**：「存活競賽」預設了達爾文敘事，看不到需求面、互補性、總產出——AI 把餅做大或做小這件事被排除了。

### v2 的核心提問

> **在 AI 前沿持續擴張下，勞動市場會浮現哪些不同的重組「體制」（regimes）——平穩重配置、極化塌陷、協作擴張？是什麼*條件*決定市場落入哪一種，這些體制之間是否存在臨界點（phase transition）？**

關鍵差異：依變項從「哪種特質贏」換成「市場落入哪種體制」。特質不再是被驗證的答案，而是讓不同體制浮現的**機制之一**。

三個層次重新定位為：

- **體制問題（macro，新的主軸）**：市場落入哪一種重組型態？臨界點在參數空間的哪裡？
- **動態問題（meso）**：AI 前沿擴張 × 人類逃逸 × 需求回饋，三者交錯時走出什麼軌跡？
- **個體問題（micro，降為輔助）**：在已浮現的體制下，哪種特質組合存活——**但這是觀察結果，不是設計目標。**

### 主要科學產出：體制相圖（Phase Diagram）

v2 的招牌交付物，是一張在 **「AI 成長速度 × 人類學習速度」**（或其他關鍵參數對）平面上的相圖，標出每一區會落入哪種體制、邊界（臨界線）在哪。這是 v1 完全沒有、卻最能讓評審記住的東西。

### 為什麼仍選 ABM

- 不做經濟預測，做**結構演化與體制辨識**。
- 市場動態從 agent 交互**自然浮現**——v2 才真正做到這點（v1 是假浮現）。
- 可在受控環境跑政策實驗（UBI、再教育、AI 稅）並比較體制轉移。

---

## 二、職業分類框架：四維度（**原封保留，僅補一處動態**）

> 這一節是 v1 的 A 級資產，文獻紮實、跨域泛化漂亮。v2 不動其定義，只強化第四維的動態性質，並改變它「進入模型的方式」（見第三節）。

四個維度與學術根源完全沿用 v1：

1. **數位化程度 Digitizability**——任務能否轉為符號處理？（Autor-Levy-Murnane 2003；Frey & Osborne 2017 的 perception/manipulation 瓶頸）
2. **情境依附性 Contextual Embeddedness**——任務是否嵌在特定社會關係/物理場域？（Frey & Osborne 的 social intelligence；Deming 2017）
3. **認知深度 Cognitive Depth**——需要多深的專業判斷？（Acemoglu & Autor 2011；creative intelligence 瓶頸）
4. **結構化稀缺性 Structuring Scarcity**——多少比例是把「尚未被定義的輸入」轉為「可執行的輸出」？（Polanyi's Paradox / Autor 2014；Wicked Problems / Rittel & Webber 1973；Jagged Frontier / Dell'Acqua et al. 2023）

### v2 對第四維的關鍵改造

v1 已正確指出第四維「會隨 AI 能力動態移動」。v2 把這句話**機制化**：第四維不再是任務上一個固定的分數，而是

- 一個任務**今天**落在前沿哪一側，是**隨機且需要被發現的**（見 §3.3 隨機前沿）；
- AI 每跨過一個門檻，一批「定義問題」任務被降格為「執行問題」——但**降格本身帶噪音**，所以前沿是毛邊的（jagged），不是一條乾淨的線。

這才真正把 Dell'Acqua 的「模糊性 > 複雜性」變成模型的**機制**，而非裝飾。

---

## 三、模型設計（核心重寫）

### 3.0 設計總原則

每一個 v2 的新機制，都對應一個 v1 缺席的回饋迴路：

| 新機制 | 回饋類型 | 解決 v1 的什麼病 |
|---|---|---|
| 隨機/可學習的替代性 | 不確定性 + 試誤 | 套套邏輯 |
| 擁擠效應（congestion） | **負回饋** | 「高 structuring 永遠贏」 |
| AI learning-by-doing | **正回饋** | 外生 S 曲線 |
| 需求面迴路 | 乘數 | 沒有一般均衡 |
| 企業進出（選擇） | 演化篩選 | 公司不會死 |
| 適應性預期 + 時滯 | 蛛網循環 | 完美預期、無震盪 |

### 3.1 世界架構

```
World
├── Agents
│   ├── Workers（人類）
│   ├── AI Capability Pool（AI 能力池，按任務類型）
│   └── Companies（企業，會進場/破產）
├── Task Market（任務市場，需求量內生）
├── Product Market（產品市場 ← v2 新增：價格、總需求迴路）
├── Matcher（匹配：帶噪音的試誤，不是確定式計分）
├── Belief / Expectation System（預期系統 ← v2 新增：有時滯）
├── AI Frontier Engine（前沿引擎：learning-by-doing 內生）
└── Statistics & Regime Classifier（統計 + 體制分類器 ← v2 新增）
```

### 3.2 每個 timestep 的流程（重排，含回饋）

```
1. Product Market：上一期就業/所得 → 決定本期總需求 → 各類任務需求量
   （v2 新增的需求回饋；失業會反噬需求）
2. Task Market：依需求生成任務，每個任務的「真實可替代性」是隱藏變數
3. Companies 發包；依「信念」（非真值）比較人 vs AI
4. Matcher：指派。AI 是否成功 = 抽樣（帶噪音）→ 暴露真實可替代性
5. 執行 → 產出、薪資、公司利潤
6. 回饋更新：
   - AI Frontier：被部署越多的任務，maturity 成長越快（正回饋）
   - Congestion：湧入某技能的 worker 越多，該技能工資溢酬越低（負回饋）
   - Expectations：worker/company 用「過去」的工資與成功率更新信念（時滯）
7. 選擇：利潤為負的公司破產；偶有新公司進場（策略被篩選）
8. Statistics + Regime Classifier 更新
```

> **設計原則（強化版）**：不只是「市場動態自然浮現」，而是「**沒有任何一條方程式直接寫出第六節的結論**」。

### 3.3 替代性：從確定式 → 隨機 + 可學習（**最關鍵的改動**）

v1：`substitutability = digitizability × (1 - embeddedness)`（乾淨、確定、寫死）。

v2：每個任務有一個**隱藏的**真實可替代性 `p_true`，公司事前不知道，**只能試了才知道**：

```python
# 任務生成時，p_true 是隨機的，期望值受四維影響，但有大方差（jagged frontier）
p_true = clip(
    sigmoid(  w_d*digitizability
            - w_e*contextual_embeddedness
            - w_s*structuring_scarcity * (1 - ai_maturity[task_type])
            + noise(scale=sigma_frontier) ),   # ← 毛邊前沿的來源
    0, 1)

# 公司不知道 p_true，只有一個帶誤差的信念 belief_p（會隨觀察更新）
# AI 接手後是否成功：success ~ Bernoulli(p_true)
# 公司用成功/失敗的歷史，貝氏更新 belief_p（這就是「試誤學習」）
```

效果：

- 前沿是**隨機毛邊**的——直接操作化 Dell'Acqua 的「模糊性」。
- 公司會**犯錯**（把 AI 派去做它其實做不好的任務，反之亦然）→ 浪費、回流、重新雇人。
- 「結構化稀缺性值錢」**不再被保證**，而是要在試誤中由市場發現——它可能成立，也可能在某些參數下不成立。**這才叫發現。**

`sigma_frontier`（前沿模糊度）本身是要掃描的關鍵參數。

### 3.4 AI Frontier：learning-by-doing（內生化）

v1：maturity 是外生 S 曲線。v2：**部署量驅動成長**（正回饋 → 臨界點）。

```python
# 某任務類型被 AI 執行得越多，它在該類型上成熟越快
ai_maturity[t] += alpha * deployment_volume[t] * (1 - ai_maturity[t])
ai_cost[t]      *= exp(-beta * cumulative_deployment[t])   # 規模 → 降本
```

這讓「AI 變強」不再是天上掉下來的時鐘，而是**市場選擇的後果**：公司越愛用 AI 的領域，AI 在那越快變得不可逆。可能跑出 tipping point 與路徑依賴——事先算不出來。

可選：偶發的外生**能力跳躍**（模擬一次新模型發布），用來研究韌性與路徑依賴。

### 3.5 擁擠效應：Congestion（**負回饋，最高槓桿的湧現來源**）

直接攻擊 v1 最大的套套邏輯——「高 structuring 永遠贏」。

```python
# 某技能/任務側的工資溢酬，隨湧入的 worker 數量遞減
wage_premium[skill] = base_premium[skill] / (1 + gamma * crowding[skill])
```

當所有被替代的人都湧去當「問題框架師」，溢酬會崩。於是「高 structuring 贏」變成「**贏到大家都擠進來為止**」——自然產生**過衝與震盪**，既真實又能推翻自己的假設。這正是評審要的「反直覺發現」，而且是真的浮現，不是寫死。

### 3.6 需求面迴路：Product Market（補上一般均衡）

v1 沒有產品市場，無法判斷自動化是把餅做大還是只重分配。v2 加最小迴路：

```python
# 總所得 → 總需求；AI 降本 → 價格下降 → 需求上升（兩股力量拉扯）
aggregate_income = sum(worker_wages) + sum(ubi)        # 就業/所得
price_level      = f(unit_cost_with_AI)                 # AI 拉低成本
task_demand_next = D(aggregate_income, price_level)     # 需求函數
# 失業 → 所得↓ → 需求↓ → 二階失業（連鎖），或 降本→需求↑→擴張（良性）
```

這把「市場重組」從口號變成可測量的東西，並讓**連鎖崩潰**或**良性成長**成為可能的浮現結果。

### 3.7 Agent 設計（修訂）

```python
@dataclass
class Worker:
    skills: np.ndarray            # shape (5,)
    structuring_ability: float    # ← 注意：是否可習得是「情境參數」，不是寫死（見下）
    adaptability: float           # 學習速度
    breadth: float                # 通才 vs 專才
    reservation_wage: float       # ← v2：明確的保留工資，用於工資清算
    belief_skill_value: np.ndarray# ← v2：對各技能未來價值的「信念」（有時滯，驅動再訓練決策）
    status: str                   # employed / retraining / unemployed
    retrain_timer: int

@dataclass
class Company:
    budget: float
    belief_p: Dict                # ← v2：對各任務可替代性的信念（試誤更新，非真值）
    hiring_policy: float          # 人 vs AI 偏好 → 會被進出選擇篩選
    profit_history: List[float]   # ← v2：用於破產判定
    efficiency_pressure: float

# AI 不再是單一 agent，而是按任務類型的能力池
ai_maturity: Dict[task_type, float]   # learning-by-doing 內生成長
ai_cost:     Dict[task_type, float]   # 規模降本
```

**worker → task 生產函數（v1 缺、v2 補明確）**：v1 的五維技能向量與四維任務之間沒有橋。v2 明確定義人類在某任務上的產出：

```python
human_output(worker, task) = (
    skill_match(worker.skills, task.skill_requirement)     # 技能契合
    * structuring_contribution(worker.structuring_ability, # 結構化貢獻
                               task.structuring_scarcity)
    * embeddedness_bonus(task.contextual_embeddedness)     # 情境加成
)
```

### 3.8 工資清算（v1 缺，v2 補）

v1 只說「供需影響」，但 Gini 完全取決於工資規則。v2 明確採用**保留工資 + 供需出清**：

```python
# 每類技能的工資由該技能的任務需求量 / 可勝任 worker 數決定
wage[skill] = clear(demand_for_skill, supply_of_skill, reservation_wages)
# 低於保留工資 → worker 寧可進入再訓練或失業
```

### 3.9 匹配與替代（修正單位 + 信念化）

v1 的 `score_ai` 與 `score_human` 不同尺度，sigmoid 差被任意縮放主宰。v2 正規化，且公司用**信念**而非真值決策：

```python
# 兩者先正規化到可比尺度（除以各自的截面均值或標準化）
value_if_AI    = expected_output_AI(belief_p[task]) / ai_cost[task_type]
value_if_human = expected_output_human(worker) / wage[skill]

# 溫度（決定轉變是平滑還是突崩）是要掃描的關鍵參數，不是常數
P(assign_AI) = sigmoid( (value_if_AI - value_if_human) / temperature )

# 制度延遲（合約、法規、信任）可按產業異質
effective = P(assign_AI) * delay_factor(industry, tau)
```

### 3.10 structuring_ability：固定還是可習得？（升為情境參數）

v1 沒交代，但這決定一切：固定 → 階級世襲；可習得 → 完全不同的動態。v2 把它變成**要對比的情境**：

```python
STRUCTURING_MODE = "innate" | "learnable_slow" | "learnable_fast"
# 三種模式各跑一遍，看體制如何不同
```

---

## 四、研究假設與情境（改為可證偽 + 體制掃描）

### 4.1 可證偽的假設（每條都附「什麼觀察會推翻它」）

> v1 的假設 A/B/C 方向對，但模型跑不出反例（因為答案寫死）。v2 要求：模型在原理上**必須有能力**產生反例。

- **H1（中段塌陷）**：AI 降本速度 > 人類學習速度時，「高數位化 × 低結構化稀缺」的中段最先崩潰。
  *證偽*：若在該參數區，中段就業率不顯著低於兩端 → H1 倒。（v2 能跑出此反例，因替代性是隨機發現的）
- **H2（結構化溢酬）**：高 structuring worker 在 AI 快速成長下薪資**上升**。
  *證偽*：**擁擠效應**可能讓溢酬先升後崩——若崩，H2 的「單調上升」被推翻，浮現「先升後崩」第三種型態。
- **H3（政策只延後不改變）**：再教育補貼延遲失業波，但不改變最終結構分佈。
  *證偽*：若需求迴路存在，補貼撐住所得 → 撐住需求 → 可能改變**最終**分佈而非僅延後。
- **H4（新假設，v2 才問得出）**：AI learning-by-doing 會產生**路徑依賴**——早期公司的隨機選擇，決定哪些領域不可逆地被自動化。
  *證偽*：若不同隨機種子收斂到同一結構 → 無路徑依賴。

### 4.2 三種情境（保留，但結果欄改為「待觀察」）

| 情境 | AI 成長速度 | 人類學習速度 | v1 的「預期」 → v2 的態度 |
|---|---|---|---|
| 慢替代 | 低 | 中 | v1 寫「平穩過渡」→ v2：**待相圖判定** |
| 快替代 | 高 | 低 | v1 寫「結構性失業」→ v2：可能因需求崩潰更糟，或因新任務緩衝更輕 |
| 協作型 | 高 | 高 | v1 寫「新職業出現」→ v2：擁擠效應可能讓協作紅利被稀釋 |

> 改動理由：v1 把「預期結果」寫進表格，等於又一次預告答案。v2 只標情境，結果交給相圖。

### 4.3 產業代表性（沿用 v1 四類）

實體服務（水電/美髮）、知識密集（法律/財務）、創意（設計/廣告）、軟體開發——四維座標沿用 v1 §三的範例表，不重複。

---

## 五、開發 Roadmap（重排，先讓回饋迴路跑起來）

> 改動理由：v1 的 roadmap 把「AI 演化」放到 Phase 3 才加，前兩期都是寫死的世界，容易先驗證了套套邏輯就停手。v2 提前讓**至少一個回饋迴路**上線。

### Phase 0：定義可證偽假設（不寫 code）
寫下 H1–H4，**並對每條寫出「什麼模擬輸出會推翻它」**。確認模型有能力產生那個反例。

### Phase 1：骨架 + 隨機前沿（約 2 週）
- 5 種任務類型；替代性是**隱藏 p_true + 公司信念**（不是確定式）。
- 公司**試誤**指派，貝氏更新信念。
- **目標輸出**：`employment_rate over time`，並確認替代曲線是**毛邊**的（證明前沿隨機性在運作）。

### Phase 2：人的複雜性 + 工資清算 + 擁擠效應（約 2–3 週）
- 四維 worker 生產函數、保留工資、供需出清。
- **擁擠效應上線**（這是最便宜的湧現來源，務必早做）。
- **新輸出**：技能別薪資曲線、Gini、structuring 溢酬曲線（看它會不會先升後崩）。

### Phase 3：AI 內生演化 + 需求迴路（約 1–2 週）
- AI learning-by-doing（部署驅動成熟）+ 規模降本。
- Product Market 需求迴路上線。
- **這時「三條曲線交錯 + 回饋」才會跑出 v1 想要、但 v1 跑不出的東西。**

### Phase 4：企業進出 + 政策實驗 + 相圖（約 1–2 週）
- 公司破產/進場（策略被選擇）。
- 政策 A/B：UBI、再教育補助、AI 稅——比較**體制轉移**，不只比 Gini。
- **掃描參數平面，產生體制相圖（招牌交付物）。**

---

## 六、預期觀察到的社會現象（**改為「候選浮現型態」**）

> 最重要的態度改變：v1 把這節當「結論」，v2 把它當「**模型有能力產生、但需由模擬證實或推翻的候選型態**」。每一項都可能在某些參數下不出現。

1. **中段塌陷（Hollowing Out）**——可能出現；但若需求迴路撐住、或前沿噪音大，中段未必最慘。
2. **結構化溢酬的非單調**——v1 預測單調上升；v2 預期**擁擠效應導致先升後崩**，這才是真正反直覺且非寫死的發現。
3. **過渡性失業波 + 二階連鎖**——v2 因需求迴路，可能放大成連鎖崩潰，或因新任務緩衝而平滑。
4. **新職業浮現**——但 v2 要求機制（Acemoglu-Restrepo reinstatement）：新任務從**前沿被自動化後釋放的人力 + 需求** 內生產生，而非外生塞入。
5. **路徑依賴與不可逆**（H4，全新）——learning-by-doing 讓早期隨機選擇鎖定長期結構。
6. **體制間的臨界轉移**——相圖上的相變線：參數微小變化導致市場從「協作擴張」突然翻入「極化塌陷」。

---

## 七、技術建議

### 語言與工具
- **Python**；ABM 用 **Mesa** 或純 numpy（輕量，推薦先 numpy 求快）。
- 視覺化：matplotlib + **Streamlit**（拉 slider 調 AI 成長/前沿噪音/擁擠強度，即時看體制變化）。
- **相圖**：跑參數網格 × 多隨機種子，用體制分類器標色。

### 資料結構（沿用 + 新增）
```python
SKILL_TYPES = ["writing", "coding", "design", "analysis", "communication"]
TASK_DIMENSIONS = ["digitizability", "contextual_embeddedness",
                   "cognitive_depth", "structuring_scarcity"]
# v2 新增的關鍵掃描參數
SWEEP_PARAMS = ["ai_growth_rate", "human_learning_rate",
                "sigma_frontier",      # 前沿模糊度
                "gamma_congestion",    # 擁擠強度
                "temperature",         # 替代轉變陡度
                "demand_elasticity"]   # 需求回饋強度
```

### 核心輸出指標（升級）
```python
stats = {
    "employment_rate": ...,
    "gini_coefficient": ...,
    "skill_wage_curves": ...,
    "structuring_premium_curve": ...,   # ← 看先升後崩
    "state_transition_matrix": ...,     # ← worker 狀態轉移
    "frontier_position": ...,           # ← 人類側佔總任務價值比例
    "replacement_rate_by_dim": ...,
    "new_job_creation": ...,            # 內生機制下的新任務速率
    "regime_label": ...,                # ← 體制分類器輸出
}
```

### 驗證（v1 缺，v2 必備）
ABM 的可信度來自**重現已知 stylized facts**。先用歷史資料校準：Autor 的職業極化、就業份額變化。模型在「已知該長什麼樣」的地方長對，未知區的相圖才有人信。**無校準 = 無說服力。**

---

## 八、關鍵參考文獻（沿用 v1，新增需求/演化機制）

| 文獻 | 核心貢獻 | 對應維度 / 機制 |
|---|---|---|
| Autor, Levy & Murnane (2003) | Routine vs non-routine | 數位化程度 |
| Frey & Osborne (2017) | 三個工程瓶頸 | 情境依附性、認知深度 |
| Acemoglu & Restrepo (2018) | Task-based、reinstatement channel | **新職業內生機制（§6.4）** |
| Autor (2014) | Polanyi's Paradox | 結構化稀缺性（根源） |
| Rittel & Webber (1973) | Wicked / ill-structured problems | 結構化稀缺性（定義） |
| Dell'Acqua et al. (2023) | Jagged frontier，模糊性 > 複雜性 | **隨機前沿 §3.3（機制化）** |
| Deming (2017) | 社交技能的持久價值 | 情境依附性 |
| Arthur (1989) | 報酬遞增與路徑依賴（lock-in） | **AI learning-by-doing §3.4（新增）** |

---

## 附錄：v1 → v2 改動速查

| 主題 | v1 | v2 | 為什麼 |
|---|---|---|---|
| 核心提問 | 什麼特質讓人存活 | 市場落入哪種**體制**、臨界點在哪 | 去套套邏輯、去零和框架 |
| 替代性 | 確定式公式 | 隱藏 p_true + 信念試誤 | 讓前沿真正毛邊、讓公司會犯錯 |
| AI 成熟 | 外生 S 曲線 | 部署驅動（learning-by-doing） | 內生 → 臨界點/路徑依賴 |
| 高 structuring | 永遠值錢（寫死） | 受**擁擠效應**反噬 | 最高槓桿的真湧現 |
| 需求面 | 無 | Product Market 迴路 | 才能談「重組」、連鎖崩潰 |
| 工資 | 「供需影響」（空） | 保留工資 + 供需出清 | Gini 才有根據 |
| 公司 | 不會死 | 進出 + 策略被選擇 | 演化篩選 |
| 預期 | 完美 | 信念 + 時滯 | 蛛網震盪 |
| 第六節 | 「結論」 | 「候選浮現型態」 | 由模擬證實/推翻 |
| 招牌產出 | 無 | **體制相圖** | 評審記得住的東西 |
| 驗證 | 無 | 對齊歷史 stylized facts | 可信度 |

---

*本文件為 v1 的修訂版。核心精神：把寫死的計分函數，換成帶回饋、帶擁擠、帶隨機前沿的交互系統——讓模型有能力跑出連設計者都沒預期的過程與結論。*
