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
        - **第一週** 目前已放入「任務01｜智慧戰略圖」
        - 其餘週次會隨課程進度陸續補上
        """
    )
    st.info("💡 點擊上方分頁按鈕切換各週內容。")

# ============================================================
# 第一週：任務01｜智慧戰略圖
# ============================================================
with tab_w1:
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
