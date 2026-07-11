import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="我的自學歷程", layout="wide", page_icon="🖌️")

# ============================================================
# 設計代幣（Design Tokens）：古風配色 —— 墨黑底 × 朱紅印璽 × 泥金
# ============================================================
INK = "#130f0b"
PANEL = "#1d1710"
PANEL_LIGHT = "#2a2116"
BORDER = "#4a3b26"
JADE = "#c23b2c"
TEAL = "#4a6b58"
GOLD = "#c9a15a"
RUST = "#8b6f47"
TEXT = "#f1e9d6"
MUTED = "#a08e6c"
PALETTE = [JADE, GOLD, TEAL, RUST, "#b23a2f", "#8a9a7e"]

# ============================================================
# 全域 CSS
# ============================================================
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/earlyaccess/cwtexkai.css');
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

html, body, [class*="css"], table, th, td, input, textarea, button, div, span, p, label {{
    font-family: "cwTeXKai", "Noto Sans TC", serif !important;
}}
h1, h2, h3 {{
    font-family: "cwTeXKai", serif !important;
    letter-spacing: 0.02em;
}}
[data-testid="stDataFrame"] * {{
    font-family: "cwTeXKai", serif !important;
    letter-spacing: 0.02em;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid {BORDER};
    flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
    color: {MUTED};
    font-weight: 500;
    padding: 10px 14px;
}}
.stTabs [aria-selected="true"] {{
    color: {JADE} !important;
    font-weight: 700;
    border-bottom: 2px solid {JADE} !important;
}}

[data-testid="stMetricValue"] {{
    color: {JADE};
    font-family: "cwTeXKai", serif;
}}
[data-testid="stMetricLabel"] {{
    color: {MUTED};
}}

hr {{
    border-color: {BORDER} !important;
    position: relative;
    margin: 20px 0 !important;
}}
hr::after {{
    content: "❖";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    background: {INK};
    color: {GOLD};
    padding: 0 14px;
    font-size: 13px;
}}

.seal-stamp {{
    position: absolute;
    top: 18px;
    right: 24px;
    width: 56px;
    height: 56px;
    background: {JADE};
    border: 2px solid {GOLD};
    border-radius: 4px;
    transform: rotate(-6deg);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
}}
.seal-stamp span {{
    color: {TEXT};
    font-family: "cwTeXKai", serif;
    font-size: 22px;
    font-weight: 700;
    writing-mode: vertical-rl;
}}

[data-testid="stSidebar"] {{
    background-color: {PANEL};
    border-right: 1px solid {BORDER};
}}

[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    overflow: hidden;
}}

[data-testid="stExpander"] {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
}}

.stDownloadButton button, .stLinkButton a {{
    background-color: {PANEL_LIGHT} !important;
    color: {JADE} !important;
    border: 1px solid {JADE} !important;
    border-radius: 6px !important;
}}
.stDownloadButton button:hover, .stLinkButton a:hover {{
    background-color: {JADE}22 !important;
}}

label {{
    color: {MUTED} !important;
}}

.week-placeholder {{
    background: {PANEL};
    border: 1px dashed {BORDER};
    border-radius: 4px;
    padding: 48px 24px;
    text-align: center;
    color: {MUTED};
}}

@media (max-width: 640px) {{
    html, body, [class*="css"], table, th, td, input, textarea, button, p, span, label {{
        font-family: "Noto Sans TC", sans-serif !important;
    }}
    [data-testid="stDataFrame"] * {{
        font-family: "Noto Sans TC", sans-serif !important;
        font-size: 13px !important;
        letter-spacing: normal;
    }}
    h1 {{
        font-size: 22px !important;
        white-space: normal !important;
        line-height: 1.4;
    }}
    h2 {{
        font-size: 19px !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 22px !important;
    }}
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def style_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT,
        font_family="cwTeXKai, serif",
        margin=dict(t=48, b=32, l=8, r=8),
    )
    return fig


def week_placeholder(week_num):
    st.markdown(
        f"""
        <div class="week-placeholder">
            <div style="font-size: 32px; margin-bottom: 12px;">🗓️</div>
            <div style="font-size: 16px; font-weight: 700; color: {TEXT}; margin-bottom: 6px;">第{week_num}週內容尚未上傳</div>
            <div style="font-size: 13px;">敬請期待，內容準備中</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_gauge(title, value, target, suffix="%"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix, "font": {"color": TEXT, "size": 28}},
        title={"text": title, "font": {"color": MUTED, "size": 14}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": MUTED},
            "bar": {"color": JADE},
            "bgcolor": PANEL_LIGHT,
            "borderwidth": 1,
            "bordercolor": BORDER,
            "threshold": {
                "line": {"color": GOLD, "width": 3},
                "thickness": 0.85,
                "value": target,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT,
        font_family="cwTeXKai, serif",
        height=220,
        margin=dict(t=50, b=10, l=20, r=20),
    )
    return fig


st.markdown(
    "<h1 style='white-space: nowrap;'>🖌️📜🏮 我的自學歷程：八週學習紀錄</h1>",
    unsafe_allow_html=True,
)

tab_home, tab_w1, tab_w2, tab_w3, tab_w4, tab_w5, tab_w6, tab_w7, tab_w8 = st.tabs([
    "🏠 首頁",
    "第一週",
    "第二週",
    "第三週",
    "第四週",
    "第五週",
    "第六週",
    "第七週",
    "第八週",
])

# ============================================================
# 首頁
# ============================================================
with tab_home:
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #241a0f 0%, {INK} 100%);
                    border: 1px solid {BORDER};
                    padding: 40px 30px; border-radius: 4px; margin-bottom: 24px;
                    position: relative; overflow: hidden;">
            <div class="seal-stamp"><span>自學</span></div>
            <h2 style="color: {TEXT}; margin: 0 0 8px 0;">我的自學歷程控制塔</h2>
            <p style="color: {MUTED}; margin: 0; font-size: 15px;">
                以八週為單位，記錄每一週的任務、學習與成果
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🧭 使用導覽")
    st.markdown(
        """
        - 上方分頁依 **第一週～第八週** 排列，每週對應該週的任務內容與學習紀錄
        - **第一週** 目前已放入任務01、02、03、04、05
        - 其餘週次會隨課程進度陸續補上
        """
    )
    st.info("💡 點擊上方分頁按鈕切換各週內容。")

# ============================================================
# 第一週：任務01 + 任務02 + 任務03
# ============================================================
with tab_w1:
    # ---------- 任務01｜智慧戰略圖 ----------
    st.markdown("<h2 style='white-space: nowrap;'>🗺️ 第一週｜任務01：智慧戰略圖</h2>", unsafe_allow_html=True)
    st.caption("Smart Strategy Map・A物流公司（綜合型3PL）")
    st.markdown("**任務目標**：為A物流公司（綜合型3PL：貨運×冷鏈）畫一張A4的「智慧戰略圖」，展開「顧客→指標→手段」三層邏輯。")

    st.divider()
    st.subheader("① 顧客側・VPC 畫布")
    vpc_data = {
        "顧客類型": ["Jobs（想完成的工作）", "Pains（困擾/痛點）", "Gains（期待的收穫）"],
        "客戶A・7-11零售連鎖": ["每日清晨4點，鮮食必到店", "早到客戶來不及，晚到斷貨", "零違約、可預測"],
        "客戶B・momo電商": ["24h內把訂單送到消費者", "高峰期延誤、退貨成本", "全鏈可視"],
        "客戶C・水產生鮮B2B": ["維持冷鏈不斷鏈", "溫控偶發異常→整批報廢", "區塊鏈級可追溯"],
        "備註": ["今日到貨、帳目清楚、冷鏈不斷", "延遲罰款、溫控異常賠償", "節省成本、提升準時率、品牌信任"],
    }
    st.table(pd.DataFrame(vpc_data).set_index("顧客類型"))

    st.subheader("② 公司側・3個可量化指標")
    kpi_data = {
        "#": [1, 2, 3],
        "指標名稱": ["庫存成本", "達交率", "冷鏈溫控達標率"],
        "定義/公式": [
            "庫存成本＝倉儲成本＋保管成本",
            "達交率＝準時交貨訂單數／總訂單數",
            "達標率＝符合溫控標準批數／總批數",
        ],
        "單位/目標值": ["≤ NT$500,000／月", "≥ 98%", "≥ 99%"],
        "KRI/KPI": ["KRI（落後）", "KPI（領先）", "KPI（領先）"],
        "判斷理由": [
            "通常在一段期間結束後才能確認",
            "發現下降可立即調整",
            "運輸途中異常可立即介入",
        ],
    }
    st.table(pd.DataFrame(kpi_data).set_index("#"))

    st.subheader("③ 管理手段・流程/人力/技術")
    action_data = {
        "類別": ["流程 Process", "人力 People", "技術 Tech"],
        "手段名稱": ["冷鏈物流標準作業流程（SOP）", "冷鏈物流人員教育訓練", "IoT溫度監控與GPS配送管理系統"],
        "具體作法/第一步": [
            "制定從入庫、儲存、揀貨、裝車、運輸到交貨的標準流程",
            "定期培訓倉儲人員及配送司機，內容包含冷鏈作業規範",
            "導入即時溫度感測器、GPS車輛定位及異常警示系統",
        ],
        "對應指標編號": ["#2、#3", "#2、#3", "#1、#2、#3"],
    }
    st.table(pd.DataFrame(action_data).set_index("類別"))

    st.subheader("④ 自評對照 Rubric")
    rubric_data = {
        "自評維度": ["①顧客洞察", "②指標+KRI/KPI區辨", "③管理手段對應"],
        "良好（75-89）": [
            "三家客戶，痛點區隔清楚",
            "3個指標含單位與目標值；至少1KRI+1KPI，含冷鏈一項",
            "流程/人力/技術三類齊全",
        ],
        "優異（90-100）": [
            "痛點含量化證據或觀察細節",
            "每個指標附簡短理由，說明為何歸類為KRI或KPI",
            "手段與KPI一對一對應且可驗證",
        ],
    }
    st.table(pd.DataFrame(rubric_data).set_index("自評維度"))

    # ---------- 任務02｜價值原型機 ----------
    st.divider()
    st.markdown("<h2 style='white-space: nowrap;'>📊 任務02｜價值原型機</h2>", unsafe_allow_html=True)
    st.caption("Data → Question → Decision")
    st.markdown(
        "**任務目標**：延續任務01的A物流公司情境，從「資料」推到「決策」，完成一頁《資料→問題→決策》反思。\n\n"
        "**資料檔**：訂單配送_202501-202506.csv、冷鏈溫控_202501-202506.csv"
    )

    st.subheader("Step 1｜掃資料（5 min）")
    scan_data = {
        "檔案": ["訂單配送", "冷鏈溫控"],
        "欄位數/筆數": ["10欄／815筆", "8欄／1,215筆"],
        "明顯異常觀察": [
            "order_id重複：15個重複ID，其中10列整列重複，刪除整列重複，ID撞號保留並可由note追蹤；"
            "order_date格式不一：Excel序號+slash/dash兩式，共44筆Excel序號（如45749），統一為YYYY-MM-DD；"
            "ship/delivery_datetime格式不一致，190筆slash式，統一為YYYY-MM-DD HH:MM:SS",
            "record_id完全重複列：15列整列重複，已刪除重複保留首筆；"
            "timestamp格式不一致：3種格式（YYYY-MM-DD/YYYY/MM/DD/DD-Mon-YYYY），統一為YYYY-MM-DD HH:MM:SS；"
            "vehicle_id空值：32列去重後無車輛代號，標為UNKNOWN無法回填；"
            "temp_zone標籤雜亂：同區有12種寫法（冷凍/冷凍/FROZEN/冷凍(-18°C)等），正規化為冷凍/冷藏/多溫層",
        ],
    }
    st.table(pd.DataFrame(scan_data).set_index("檔案"))

    st.subheader("Step 2a｜Meta-prompt")
    st.markdown(
        "> 你是一位資深3PL物流營運顧問。我是綜合型3PL（貨運常溫+冷鏈倉儲）的營運分析師見習生。"
        "我手上有兩份資料：訂單配送（815筆，欄位：order_id、order_date、ship/delivery_datetime、"
        "customer_id/name、region、temp_layer、qty、freight_twd）與冷鏈溫控（1,215筆，欄位：record_id、"
        "timestamp、vehicle_id、temp_zone、target_temp_low/high_c、temp_c、pass_flag）。請：\n"
        "> 1. 提出3個最有價值的「跨業務線（貨運×冷鏈）」管理問題，並說明為何重要。\n"
        "> 2. 每題標明用到哪些欄位、來自訂單檔還是冷鏈檔。\n"
        "> 3. 區分每題屬BI（描述/異常）還是AI（預測/最佳化），並說明理由。\n"
        "> 4. 最後反問我一個你認為我忽略的關鍵問題。\n"
        "> 請勿直接幫我算數字，重點在「問對問題」。"
    )

    st.subheader("Step 2b｜3個跨業務線管理問題")
    q_data = {
        "#": [1, 2, 3],
        "管理問題": [
            "冷鏈溫控異常是否影響配送效率與準時送達？",
            "哪些地區或溫層的配送成本較高且冷鏈異常較多？",
            "未來哪些配送最可能發生冷鏈異常或配送延誤？",
        ],
        "用到欄位（標檔）": [
            "訂單配送：region、ship_datetime、delivery_datetime、temp_layer；冷鏈溫控：timestamp、temp_c、pass_flag",
            "訂單配送：region、temp_layer、qty、freight_twd；冷鏈溫控：temp_zone、pass_flag",
            "訂單配送：region、ship_datetime、delivery_datetime、temp_layer 等",
        ],
        "BI/AI": [
            "BI／分析溫控異常是否與配送延誤有相關性",
            "BI／比較不同區域、不同溫層的成本與異常率",
            "AI／利用歷史配送與溫控資料建立預測模型",
        ],
    }
    st.table(pd.DataFrame(q_data).set_index("#"))

    st.subheader("Step 2c｜與講師版本對照")
    compare_data = {
        "對照題": ["哪裡一致", "哪裡不同", "哪個比較好"],
        "你的觀察": [
            "兩個版本的核心內容其實是一樣的：①冷鏈異常是否影響配送效率；②哪些區域/溫層成本高且異常多",
            "1. 管理問題：講師版有說明背景，內容較完整；自己版問題簡潔，一句話就能看懂。"
            "2. 用到欄位：自己版有分訂單檔、冷鏈檔",
            "我選擇這三個管理問題，是因為它們同時涵蓋服務品質、成本控制與風險預防三個核心管理面向，"
            "且都需要結合貨運與冷鏈資料分析，比單一業務線的問題更貼近綜合型3PL的實際營運需求",
        ],
    }
    st.table(pd.DataFrame(compare_data).set_index("對照題"))

    st.subheader("Step 3｜寫心得（資料→問題→決策）")
    reflect_data = {
        "項目": ["資料（Data）", "問題（Question）", "決策（Decision）"],
        "內容": [
            "蒐集並整理訂單配送（配送時間、配送區域、溫層、數量等）與冷鏈溫控資料",
            "從資料中找出管理問題，例如：①冷鏈溫控異常是否影響配送效率",
            "根據分析結果，制定改善措施，例如：優化配送路線、加強溫控監測",
        ],
    }
    st.table(pd.DataFrame(reflect_data).set_index("項目"))

    st.markdown("**我的判斷**：部分同意 AI 的分析")
    st.info(
        "我部分同意AI的分析，因為AI能快速從訂單配送與冷鏈溫控資料中找出值得關注的管理問題，"
        "提供分析方向；但目前資料缺少訂單與冷鏈之間的共同關聯欄位，且部分資料存在品質問題，"
        "仍需人工判斷驗證後才能做出最終決策。"
    )

    # ---------- 任務03｜燃料提煉廠 Worksheet ----------
    st.divider()
    st.markdown("<h2 style='white-space: nowrap;'>🏭 任務03｜燃料提煉廠 Worksheet</h2>", unsafe_allow_html=True)
    st.caption("雙CSV清洗＋業務報告（W1 Day2）")
    st.markdown(
        "適用於 Week1・Day2／預估填寫時間：全日穿插填寫，15:00前彙整\n\n"
        "**本版重點**：訂單CSV與冷鏈CSV流程完全分章，避免互混"
    )

    st.subheader("〔Section 0〕雙CSV流程速覽")
    s0_data = {
        "CSV": ["訂單CSV", "冷鏈CSV"],
        "章節": ["Section A", "Section B"],
        "出檔": ["A_物流_訂單配送_CLEAN.csv", "A_物流_冷鏈溫控_CLEAN.csv"],
        "流程": ["覆蓋率／準確度／時效／主資料治理", "感測器故障／時戳解析／pass_flag重算／異常集中"],
    }
    st.table(pd.DataFrame(s0_data).set_index("CSV"))
    st.caption("本日清洗兩份CSV，兩份各自獨立流程，不要互混；建議節奏：早上Section A（訂單），下午Section B（冷鏈），Section C才整合算KPI")

    st.subheader("〔Section 1〕觀念回顧")
    st.markdown("**1.1 五件套 Prompt（讓AI當助教）**")
    prompt5_data = {
        "件": ["角色", "診斷", "分階段", "回報", "驗收"],
        "內容": [
            "我是物流公司的分析師",
            "目前我的環境是有VS Code跟Python，發生的問題是有髒資料",
            "「請分幾個步驟教，每步問我做完了沒」",
            "「我會把每步的結果（指令輸出）貼給你」",
            "「最後給我三行驗證指令確認OK」",
        ],
    }
    st.table(pd.DataFrame(prompt5_data).set_index("件"))

    st.markdown("**1.2 品質三問（資料清洗框架）**")
    q3_data = {
        "問": ["覆蓋率", "準確度", "時效"],
        "工具": [".isna().sum() / drop_duplicates / 主鍵衝突", ".value_counts() / 異常值 / 格式統一", "邏輯檢查 / 未來日期 / 時戳順序"],
        "物流例子": ["訂單缺customer_id", "溫層6種寫法", "送達早於出貨"],
    }
    st.table(pd.DataFrame(q3_data).set_index("問"))

    st.markdown("**1.3 5種以上髒資料模式**")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("- **缺漏**：哪些欄位有空白")
        st.markdown("- **異常值**：數量、金額不合理")
        st.markdown("- **時序錯亂**：時間邏輯不合理")
    with c2:
        st.markdown("- **重複**：region缺24、qty缺15、freight_twd缺37")
        st.markdown("- **格式不一**：freight_twd負數12筆；另有qty=-64")
        st.markdown("- **第6種（自選）**：送達早於出貨5筆")

    st.divider()
    st.subheader("Section A｜訂單CSV清洗（09:50-12:00）")
    st.caption('載入：df_orders = pd.read_csv("A_物流_訂單配送_202501-202506.csv")，預期815筆')

    st.markdown("**A-§A 覆蓋率（25 min）**")
    aa_data = {
        "步": [1, 2, 3, 4, 5, 6],
        "動作": [
            "文字去空白 .str.strip()", "空字串轉NaN replace('', np.nan)",
            "關鍵欄位缺漏刪（order_id/customer_id）", "數值缺漏用同溫層中位數補freight_twd",
            "完全重複列 drop_duplicates()", "主鍵衝突（同order_id兩筆，選qty大者）",
        ],
        "移除筆數": ["0筆", "0筆", "15筆", "0筆", "－", "0筆"],
        "判斷理由": [
            "去除前後空白，統一格式", "統一缺漏值格式，方便後續處理",
            "無法唯一識別訂單或客戶，因此刪除", "正常配送數量與運費不應為負數，可能是輸入錯誤或退貨",
            "完成資料清洗後輸出清洗檔，供後續分析使用",
            "order_id應代表唯一訂單，若重複代表可能重複匯入",
        ],
    }
    st.table(pd.DataFrame(aa_data).set_index("步"))

    st.markdown("**A-§B 準確度（45 min）**")
    ab_data = {
        "步": [1, 2, 3],
        "動作": ["負數運費 freight_twd.abs()", "溫層歸一（6種寫法統一）", "日期格式統一 pd.to_datetime(errors='coerce')"],
        "處理筆數": ["12筆", "0筆", "0筆"],
        "判斷理由": [
            "配送運費通常不應為負值，負值可能是輸入錯誤或退貨",
            "同一溫層有多種寫法（如AMBIENT、常溫、CHILLED等）",
            "原始資料同時存在三種日期格式，需統一轉為datetime",
        ],
    }
    st.table(pd.DataFrame(ab_data).set_index("步"))
    st.info("溫層6種寫法歸一檢核：冷藏／冷藏區／冷藏(2-8°C)／chilled／CHILLED 全部統一成「冷藏」")

    st.markdown("**A-§C 時效（40 min）**")
    ac_data = {
        "步": [1, 2],
        "動作": ["ship_datetime ≤ delivery_datetime 邏輯檢查", "未來日期（order_date > 2026-06-30）剔除"],
        "標記/刪除筆數": ["25筆", "7筆"],
        "立場": ["標記", "標記"],
    }
    st.table(pd.DataFrame(ac_data).set_index("步"))
    st.caption("講義立場：時戳錯序標記不刪（可追蹤）；未來日期剔除（違反時序因果）")

    st.markdown("**A-§D 主資料治理（50 min）**")
    ad_data = {
        "步": [1, 2],
        "動作": ["customer_name.value_counts() 看momo5種寫法", "以customer_id為Master歸一customer_name"],
        "結果": ["發現同一客戶有多種寫法，例如momo購物網、MOMO等", "customer_id為客戶唯一識別碼，以其作為主資料依據"],
    }
    st.table(pd.DataFrame(ad_data).set_index("步"))

    st.success("✅ A段出檔檢核：產出 A_物流_訂單配送_CLEAN.csv（預期約800筆）；我的CLEAN共800筆（原815-移除15+補回0=800）；df_orders.isna().sum() 全部=0（自我驗收）")

    st.divider()
    st.subheader("Section B｜冷鏈CSV清洗（14:00-14:50）")
    st.caption('載入：df_cold = pd.read_csv("A_物流_冷鏈溫控_202501-202506.csv")，預期1,215筆')

    b_data = {
        "步驟": [1, 2, 3, 4, 5],
        "動作": [
            "刪 record_id/timestamp 缺失", "完全重複列",
            "感測器故障標記（999/-999/99.9）→ sensor_fault_flag=1, temp_c=NaN",
            "時戳多格式解析，失敗者刪", "其他關鍵欄（vehicle_id）空值：dropna（temp_c故障NaN保留）",
        ],
        "移除/標記筆數": ["32筆/0筆", "15筆", "0筆/51筆", "0筆", "32筆/0筆"],
        "判斷理由": [
            "UNKNOWN/無法解析", "刪除",
            "哨兵值不代表真實溫度，將temp_c設為NaN",
            "無法解析：0筆，所以沒有資料被刪除", "缺失標記/UNKNOWN",
        ],
    }
    st.table(pd.DataFrame(b_data).set_index("步驟"))
    st.success("✅ B段出檔檢核：產出 A_物流_冷鏈溫控_CLEAN.csv（預期約1,200筆）；我的CLEAN共1200筆；df_cold.isna().sum() 確認剩餘NaN都是故障標記後刻意NaN的temp_c")

    st.divider()
    st.subheader("Section C｜整合＋業務報告（14:50-15:45）")

    st.markdown("**C.1 三個業務數字（儀表板檢視）**")

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.plotly_chart(make_gauge("基礎達交率", 95, 95), width="stretch")
        st.caption("目標 ≥95%　金線＝目標門檻")
    with kpi_col2:
        st.plotly_chart(make_gauge("冷鏈溫控達標率", 99.5, 99.5), width="stretch")
        st.caption("目標 ≥99.5%")
    with kpi_col3:
        st.plotly_chart(make_gauge("Top20%客戶運費占比", 80, 80), width="stretch")
        st.caption("驗證80/20法則")

    st.markdown("**C.2 清洗稽核日誌.md（主交付物）**")
    st.code(
        "# 任務03清洗稽核日誌\n\n"
        "## 訂單CSV（原815筆）\n"
        "- §A覆蓋率：移除15筆，主因完全重複列及同一order_id重複，避免重複計算\n"
        "- §B準確度：處理12筆，主因負運費、統一溫層寫法、統一日期格式，提高分析準確性\n"
        "- §C時效：標記32筆，刪除0筆，主因保留異常資料供後續人工確認",
        language="markdown",
    )

    st.markdown("**C.3 業務對話演練（對總經理的話——結論＋三方向）**")
    c3_data = {
        "段": ["1句話結論", "三個方向擇1調查", "接D3預告"],
        "內容": [
            "本次完成訂單配送與冷鏈溫控資料的清理與標準化，建立可供分析的資料基礎",
            "1. 提升配送效率　2. 強化冷鏈品質管理　3. 優化客戶與配送成本",
            "明天Day3儀表板會用這三個切面同時秀給您看",
        ],
    }
    st.table(pd.DataFrame(c3_data).set_index("段"))

    st.markdown("**〔評分對照〕**")
    score_data = {
        "維度": ["覆蓋率（訂單§A+主鍵衝突）", "準確度（訂單§B+Excel序列日期）", "時效（訂單§C標記+剔未來日期）",
                "主資料治理（訂單§D+Master邏輯）", "冷鏈清洗（Section B）", "稽核日誌（每步+判斷理由+KPI）", "總計"],
        "配分": [20, 20, 20, 15, 15, 10, 100],
        "我的得分": [15, 15, 15, 5, 5, 5, 60],
    }
    st.table(pd.DataFrame(score_data).set_index("維度"))

    # ---------- 任務04｜現況儀表板 ----------
    st.divider()
    st.markdown("<h2 style='white-space: nowrap;'>📟 任務04｜現況儀表板</h2>", unsafe_allow_html=True)
    st.caption("給總經理30秒讀")
    st.markdown("適用：Week1・Day3／2026起用　　預估填寫時間：100分鐘（含互看與pitch）")

    st.subheader("Section 1｜觀念回顧")
    st.markdown("**1.1 四階分析階梯**")
    ladder_data = {
        "階": ["1. Descriptive", "2. Diagnostic", "3. Predictive", "4. Prescriptive"],
        "問題": ["發生了什麼？", "為什麼發生？", "將會發生什麼？", "該怎麼辦？"],
        "典型產出": ["儀表板、報表、統計摘要", "異常下鑽、關聯分析", "預測模型", "最佳化建議、AI代理"],
        "本日目標": ["今天主場", "W1收尾", "W3", "W4-W7"],
    }
    st.table(pd.DataFrame(ladder_data).set_index("階"))

    st.markdown("**1.2 描述性統計三把刀**")
    stat3_data = {
        "把刀": ["集中：Mean／Median／Mode", "離散：Std／IQR／全距", "分布：看直方圖"],
        "重點問答": [
            "何時用Median？→ 分布對稱時／有極端值時／類別型資料",
            "IQR是Q3-Q1，代表 → 離平均的平均距離／Q3-Q1，中間50%的範圍／max-min",
            "是否常態及是否長尾 → 物流資料幾乎都有長尾：少數大客戶占大比例運費，長尾＝80/20法則的徵兆",
        ],
    }
    st.table(pd.DataFrame(stat3_data).set_index("把刀"))

    st.markdown("**1.3 報表 vs 儀表板四判準**")
    report_dash_data = {
        "#": [1, 2, 3, 4],
        "報表": ["月結／週結靜態", "密密麻麻", "給分析師", "答「過去」"],
        "儀表板": ["準即時更新", "30秒讀完", "給管理者", "指「現在的行動」"],
    }
    st.table(pd.DataFrame(report_dash_data).set_index("#"))

    st.subheader("Section 2｜資料來源確認（5 min）")
    st.caption("D2清洗後產出兩個*_CLEAN.csv，本日儀表板從這兩個讀：")
    src_data = {
        "CSV": ["A_物流_訂單配送_CLEAN.csv", "A_物流_冷鏈溫控_CLEAN.csv"],
        "預期欄位": [
            "order_id／customer_id／order_date／freight_twd／qty／temp_layer／ship_datetime／delivery_datetime",
            "sensor_id／vehicle_id／warehouse_id／timestamp／temp_c／pass_flag／sensor_fault_flag",
        ],
        "用途": [
            "KPI卡：總訂單數、平均運費、達交率；折線：週訂單量趨勢",
            "KPI卡：冷鏈達標率（紅字警示）；長條：車輛/倉庫排行",
        ],
    }
    st.table(pd.DataFrame(src_data).set_index("CSV"))
    st.success("✅ 訂單CLEAN我有793筆（D2末預期約800筆）；冷鏈CLEAN我有943筆（D2末預期約1200筆）；pass_flag.mean()＝73.85%（預期70-80%）")

    st.subheader("Section 3｜儀表板版面設計（15 min）")
    st.markdown("**3.1 F字型版面草稿**")
    st.code(
        "標題列\n"
        "┌────────┐ ┌────────┐ ┌────────┐\n"
        "│ KPI 1  │ │ KPI 2  │ │ KPI 3  │  ← 最左上＝最重要\n"
        "└────────┘ └────────┘ └────────┘\n\n"
        "┌──────────────┐ ┌──────────────┐\n"
        "│ 圖1（週訂單）│ │ 圖2（溫控達標）│\n"
        "│    折線圖     │ │    車輛排行    │\n"
        "└──────────────┘ └──────────────┘\n\n"
        "⚠ 預警標註：冷鏈達標率 ___%（目標 99.5%）",
        language=None,
    )

    st.markdown("**3.2 三個KPI卡規劃**")
    st.caption("★ 必須「訂單面＋冷鏈面」都覆蓋（只放訂單會被扣分）")
    kpi3_data = {
        "卡號": [1, 2, 3],
        "指標名稱": ["總訂單數", "基礎達交率", "冷鏈達標率"],
        "計算邏輯": [
            "len(df_orders)",
            "先排除異常值（ship_before_deliver_ok==False）後計算準時交貨比例",
            "排除pass_flag缺值（75筆，感測器故障或讀數異常）後計算達標比例",
        ],
        "目標值": ["無固定目標（描述性指標，反映資料量與營運規模）", "95%", "99.5%"],
        "紅字警示": ["否", "是", "是"],
    }
    st.table(pd.DataFrame(kpi3_data).set_index("卡號"))

    st.markdown("**3.3 兩張圖規劃**")
    chart2_data = {
        "圖號": [1, 2],
        "類型": ["折線", "長條"],
        "X軸": ["週（order_date依週彙總，W-SUN）", "車輛編號 vehicle_id"],
        "Y軸": ["order_date出貨數量加總 qty", "冷鏈異常次數 pass_flag=0"],
        "回答什麼問題": ["出貨量是否有高峰、低谷或趨勢？", "哪些車輛異常最多、需要優先改善？"],
    }
    st.table(pd.DataFrame(chart2_data).set_index("圖號"))

    st.subheader("Section 4｜Streamlit dashboard.py 開發（40 min・主交付物①）")
    st.markdown("**4.1 環境啟動檢核**")
    st.markdown("- ☐ `pip show streamlit` 有版本號出現")
    st.markdown("- ☑ `streamlit hello` 跑得起來")
    st.markdown("- 我的工作資料夾：`0701`")

    st.markdown("**4.2 程式骨架（沿講義範本擴充）**")
    skeleton_data = {
        "段落": [
            "st.set_page_config + st.title",
            "pd.read_csv載兩個CSV（訂單+冷鏈）",
            "3個 st.metric KPI卡",
            "2張圖（st.line_chart/st.bar_chart/st.plotly_chart）",
            "預警標註（st.error或紅字markdown）",
        ],
        "完成": ["✅", "✅", "✅", "☐", "✅"],
        "自我說明": [
            "已設定頁面標題、版面配置（寬版）及儀表板標題",
            "已成功載入訂單配送與冷鏈溫控兩份CLEAN CSV檔",
            "已建立總訂單數、基礎達交率、冷鏈達標率三個KPI卡",
            "已完成每週出貨數量折線圖，尚未加入車輛排行長條圖",
            "冷鏈達標率低於目標99.5%時，會顯示紅字警示",
        ],
    }
    st.table(pd.DataFrame(skeleton_data).set_index("段落"))

    st.markdown("**4.3 啟動驗收**")
    st.code("streamlit run dashboard.py", language="bash")
    st.markdown("- ☑ 瀏覽器自動開 http://localhost:8501")
    st.markdown("- ☑ 30秒內能看完（用碼表算）")
    st.markdown("- ☑ 紅字警示醒目")

    # ---------- 任務05｜VIP篩選器 ----------
    st.divider()
    st.markdown("<h2 style='white-space: nowrap;'>🎯 任務05｜VIP篩選器</h2>", unsafe_allow_html=True)
    st.caption("RFM八分群＋業務行動書")
    st.markdown("適用：Week1・Day4／2026起用　　預估填寫時間：100分鐘（含45分鐘分群辯論會）")

    st.subheader("Section 1｜觀念回顧（填空，5 min）")
    st.markdown("**1.1 RFM三維各代表什麼**")
    rfm_def_data = {
        "字": ["R", "F", "M"],
        "完整字": ["Recency", "Frequency", "Monetary"],
        "算法": ["今天日期－最後一次消費日期", "統計期間內的消費次數", "統計期間內的總消費金額"],
        "物流意義": ["距離最近一次下單的時間", "一段期間內下單次數", "一段期間內累積訂單金額"],
    }
    st.table(pd.DataFrame(rfm_def_data).set_index("字"))

    st.markdown("**1.2 反直覺三點（自寫）**")
    counter_data = {
        "問題": ["80/20不是鐵律——為什麼？", "At Risk比VIP更該投資資源——為什麼？", "Big Spenders≠VIP——為什麼？"],
        "我的答案": [
            "少數重要客戶通常會貢獻大部分的價值",
            "以前是重要客戶，但最近很久沒下單，有流失風險",
            "高消費客戶，不一定是VIP",
        ],
    }
    st.table(pd.DataFrame(counter_data).set_index("問題"))

    st.markdown("**1.3 八分群速查**")
    seg_data = {
        "分群": ["VIP(Champions)", "Loyal", "Big Spenders", "New／Promising",
                "Potential Loyalists", "At Risk", "Hibernating", "Lost"],
        "R": ["高", "中高", "高", "高", "高", "低", "低", "低"],
        "F": ["高", "高", "低", "低", "中", "中高", "低", "低"],
        "M": ["高", "中", "高", "低", "中", "高", "中", "低"],
        "策略": [
            "🔒鎖－指派專屬客服、優先排車、定期業務拜訪",
            "🌱養－推薦升級方案、捆綁服務",
            "⛏挖－從單次合作升到長期合約",
            "🧲引－首購優惠、流程引導",
            "🌱扶－主動詢問需求、客製化",
            "🚨救－業務經理親自拜訪、客製化回流方案",
            "⏰喚－針對節慶期主動聯絡",
            "👋放－不主動投資資源，EDM即可",
        ],
    }
    st.table(pd.DataFrame(seg_data).set_index("分群"))
    st.caption("8個策略：鎖／養／挖／引／扶／救／喚／放")

    st.subheader("Section 2｜資料準備＋觀察期決定（10 min）")
    st.markdown("**2.1 資料來源**：從D2清洗後的 A_物流_訂單配送_CLEAN.csv 算RFM")

    st.markdown("**2.2 觀察期切點（主觀但要可辯護）**")
    period_data = {
        "切點": ["觀察期起始日", "觀察期結束日（today）", "期長（月）"],
        "我的選擇": ["2025-01-01", "2026-07-01", "181天≈5.9個月"],
        "為什麼？": [
            "因為這份CSV本身就是完整的訂單紀錄，資料涵蓋的範圍就是完整的觀察窗口",
            "如果直接拿max(order_date)當today，最新訂單的客戶R值會被算成0，造成偏誤",
            "以today=pd.Timestamp('2026-07-01')為基準日，計算所有客戶的R值",
        ],
    }
    st.table(pd.DataFrame(period_data).set_index("切點"))
    st.caption("提示：期太短（<3個月）R/F不穩；期太長（>12個月）會被舊行為主導。物流B2B常用6個月")
    st.success("✅ 客戶數＝8位（預期8位）；訂單數＝793筆（在觀察期內）")

    st.subheader("Section 3｜RFM計算（15 min・主交付物①）")
    st.markdown("**3.1 三維計算邏輯**")
    st.code(
        'import pandas as pd\n'
        'df = pd.read_csv("A_物流_訂單配送_CLEAN.csv", parse_dates=["order_date"])\n'
        'today = pd.Timestamp("2026-07-01")\n'
        'rfm = df.groupby("customer_id").agg(\n'
        '    R=("order_date", lambda s: (today - s.max()).days),\n'
        '    F=("order_id", "count"),\n'
        '    M=("freight_twd", "sum"),\n'
        ').reset_index()',
        language="python",
    )
    rfm_result_data = {
        "customer_id": ["C001", "C002", "C003", "C004", "C005", "C006", "C007", "C008"],
        "customer_name": ["7-11零售連鎖", "momo購物網", "水產鮮活B2B", "家樂福全聯",
                          "蝦皮購物", "全聯福利中心", "統一生鮮", "PChome 24h"],
        "R": [1, 1, 1, 1, 1, 2, 1, 1],
        "F": [88, 103, 108, 82, 95, 93, 115, 109],
        "M": [199084.4, 232622.3, 245576.3, 171144.1, 199303.3, 215567.8, 270698.4, 222216.5],
    }
    st.table(pd.DataFrame(rfm_result_data).set_index("customer_id"))

    st.markdown("**3.2 5等分＋RFM_score**")
    st.code(
        'rfm["R_score"] = pd.qcut(rfm["R"], 5, labels=[5, 4, 3, 2, 1]).astype(int)\n'
        'rfm["F_score"] = pd.qcut(rfm["F"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)\n'
        'rfm["M_score"] = pd.qcut(rfm["M"], 5, labels=[1, 2, 3, 4, 5]).astype(int)\n'
        'rfm["RFM_score"] = rfm["R_score"].astype(str) + rfm["F_score"].astype(str) + rfm["M_score"].astype(str)',
        language="python",
    )
    st.warning("⚠ F用rank(method='first')是因為F容易有重複值（qcut會崩），這個處理要寫進設計說明")

    score_result_data = {
        "customer_id": ["C001", "C002", "C003", "C004", "C005", "C006", "C007", "C008"],
        "R_score": [5, 5, 4, 3, 3, 1, 2, 1],
        "F_score": [1, 3, 4, 1, 3, 2, 5, 5],
        "M_score": [1, 4, 5, 1, 2, 3, 5, 3],
        "RFM_score": ["511", "534", "445", "311", "332", "123", "255", "153"],
        "落到哪一群？": ["一般客戶", "重要價值客戶", "重要價值客戶", "需喚醒客戶",
                     "一般客戶", "一般客戶", "重要價值客戶", "穩定客戶"],
    }
    st.table(pd.DataFrame(score_result_data).set_index("customer_id"))

    st.subheader("Section 4｜分群覆蓋＋Excel名單（20 min・主交付物②）")
    st.markdown("**4.1 分群統計（必含≥5群覆蓋）**")
    coverage_data = {
        "分群": ["VIP(Champions)", "Loyal", "Big Spenders", "New／Promising",
                "Potential Loyalists", "At Risk", "Hibernating", "Lost"],
        "客戶數": [1, 0, 1, 1, 1, 2, 1, 1],
        "客戶ID": ["C003", "－", "C002", "C001", "C005", "C007、C008", "C004", "C006"],
    }
    st.table(pd.DataFrame(coverage_data).set_index("分群"))
    st.success("✅ 自我檢核：≥5群覆蓋（<5會扣分）")

    st.markdown("**4.2 Excel客戶分層名單（主交付物②）**")
    st.markdown("將Section 3.2的內容，寫進 `客戶分層名單.xlsx`，欄位設計：customer_id／name／R／F／M／RFM_score／分群／建議行動")
    st.markdown(
        "加分項（Excel進階）：\n"
        "- ✅ 條件格式：R/F/M用顏色梯度\n"
        "- ✅ pivot：分群×平均M\n"
        "- ✅ 行動優先級標色：🔴At Risk／🟢VIP"
    )

    st.subheader("Section 5｜業務行動書（20 min・主交付物③）")
    st.caption("★ 每群≥1項具體行動；Top20%與At Risk各≥3項")

    st.markdown("**5.1 Top20%（VIP／Big Spenders）—— 鎖**")
    top20_data = {
        "客戶": ["C003（水產鮮活B2B）", "C002（momo購物網）", "C003+C002（合併）"],
        "具體行動（動詞+量化）": [
            "簽訂6個月鎖價合約，目標M成長≥10%",
            "推出滿額贈禮，拉高客單價15%",
            "每月促成2項交叉銷售",
        ],
        "預期效益／月": ["月增NT$4,162（高）", "月增NT$5,914（高）", "月增NT$6,000~10,000（中）"],
        "投入成本": ["低", "中", "低"],
    }
    st.table(pd.DataFrame(top20_data).set_index("客戶"))

    st.markdown("**5.2 At Risk —— 救（★最該投資的群）**")
    atrisk_data = {
        "客戶": ["C007・統一生鮮", "C007・統一生鮮", "C007+C008（合併）"],
        "具體行動": [
            "48小時內致電了解原因，提供單筆訂單折扣",
            "主動推送3款互補品項報價單",
            "每週監控R值，連續14天無訂單自動觸發提醒",
        ],
        "預期效益／月": ["月增NT$3,670（中）", "月增NT$2,500（中）", "保住月均NT$83,545營收基礎（高）"],
        "投入成本": ["低", "低", "低"],
    }
    st.table(pd.DataFrame(atrisk_data).set_index("客戶"))

    st.markdown("**5.3 其他群（每群至少1行）**")
    other_seg_data = {
        "分群": ["Loyal", "Big Spenders", "New／Promising", "Potential Loyalists", "Hibernating", "Lost"],
        "具體行動": [
            "建立F值連續2個月≥4分自動觸發忠誠會員卡機制",
            "提供季度採購報告，找出1項高毛利加購品項",
            "7日內發送新客歡迎禮，第二筆訂單10%折扣",
            "加入訂閱式自動補貨方案",
            "每月1次EDM/簡訊喚醒活動",
            "每季1次最低成本喚回簡訊",
        ],
    }
    st.table(pd.DataFrame(other_seg_data).set_index("分群"))

    st.subheader("Section 6｜反直覺洞察（10 min）")
    st.caption("★ 評分Rubric「反直覺洞察」滿分需要3+個")
    insight_data = {
        "#": [1, 2, 3],
        "反直覺發現": [
            "訂單間隔約1天，R_score全靠rank()硬切排名撐出來，數值差異其實很小",
            "C007（訂單115次、金額NT$270,698，兩項全場最高）卻只拿到RFM_score=255而非555",
            "8大分群裡，理論上「Loyal（F_score高）」應該最多，但實際上分佈不均，甚至出現0人",
        ],
        "為什麼反直覺？": [
            "直覺上「最近有沒有買」應該是最直接、最敏感的指標，但當客戶下單頻率都很高、間隔天數接近時，R值的鑑別力反而下降",
            "一般人用「金額大＝重要客戶＝安全」的線性思維，忽略了R值（最近下單時間）同樣重要，C007其實R已經拉警報",
            "直覺認為越「中庸」的標籤人數應該越多，但F分群受限於樣本數少（僅8位客戶），反而容易出現分佈極端",
        ],
        "對誰最有用？": [
            "資料分析／報表設計人員——提醒未來若持續用同一套切分邏輯，需注意R值鑑別力的侷限",
            "業務主管／客戶關係經理——只看金額排名會誤判為安全客戶",
            "行銷企劃人員——不能直接套用「Loyal客戶要做會員經營」的通則，因為根本沒有Loyal客戶",
        ],
    }
    st.table(pd.DataFrame(insight_data).set_index("#"))
    st.info("範例：C003水產鮮活的M在Top3，但R已經90天沒下單……（高金額但即將流失，業務拜訪優先）")

# ============================================================
# 第二週～第八週：空白佔位
# ============================================================
with tab_w2:
    st.markdown("<h2>第二週</h2>", unsafe_allow_html=True)
    week_placeholder(2)

with tab_w3:
    st.markdown("<h2>第三週</h2>", unsafe_allow_html=True)
    week_placeholder(3)

with tab_w4:
    st.markdown("<h2>第四週</h2>", unsafe_allow_html=True)
    week_placeholder(4)

with tab_w5:
    st.markdown("<h2>第五週</h2>", unsafe_allow_html=True)
    week_placeholder(5)

with tab_w6:
    st.markdown("<h2>第六週</h2>", unsafe_allow_html=True)
    week_placeholder(6)

with tab_w7:
    st.markdown("<h2>第七週</h2>", unsafe_allow_html=True)
    week_placeholder(7)

with tab_w8:
    st.markdown("<h2>第八週</h2>", unsafe_allow_html=True)
    week_placeholder(8)

st.divider()
st.caption("🌱 我的自學歷程：八週學習紀錄")
