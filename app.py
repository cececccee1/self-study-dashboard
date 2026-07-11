import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="我的學習歷程", layout="wide", page_icon="🖌️")

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

# ============================================================
# 分頁導覽腳本：讓「回上一頁／返回首頁」按鈕真正切換 Streamlit 分頁
# （而不是單純捲動頁面），透過操作 st.tabs 底層的 BaseWeb tab 按鈕實現
# ============================================================
components.html(
    """
    <script>
    (function () {
      function setup() {
        try {
          var doc = window.parent.document;
          var tabs = doc.querySelectorAll('[data-baseweb="tab"]');
          if (!tabs.length) { setTimeout(setup, 300); return; }

          if (!window.parent.__tabNavSetup) {
            window.parent.__tabHistory = [];
            window.parent.__currentTab = null;

            tabs.forEach(function (tab) {
              tab.addEventListener('click', function () {
                var label = tab.innerText.trim();
                if (window.parent.__currentTab && window.parent.__currentTab !== label) {
                  window.parent.__tabHistory.push(window.parent.__currentTab);
                }
                window.parent.__currentTab = label;
              });
            });

            window.parent.goHomeTab = function () {
              var t2 = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
              for (var i = 0; i < t2.length; i++) {
                if (t2[i].innerText.indexOf('首頁') !== -1) {
                  t2[i].click();
                  break;
                }
              }
            };

            window.parent.goBackTab = function () {
              var hist = window.parent.__tabHistory;
              var target = (hist && hist.length) ? hist.pop() : null;
              var t2 = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
              if (target) {
                for (var i = 0; i < t2.length; i++) {
                  if (t2[i].innerText.trim() === target) {
                    t2[i].click();
                    return;
                  }
                }
              }
              window.parent.goHomeTab();
            };

            window.parent.__tabNavSetup = true;
          }
        } catch (e) {
          /* 靜默失敗，不影響其餘功能 */
        }
      }
      setup();
    })();
    </script>
    """,
    height=0,
)


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


def back_to_home_button():
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;
                    margin-top: 40px; margin-bottom: 8px;">
            <a href="#"
               onclick="if (window.parent.goBackTab) {{ window.parent.goBackTab(); }} return false;"
               style="display: inline-block; padding: 10px 28px; background: {PANEL_LIGHT};
                      border: 1px solid {GOLD}; border-radius: 6px; color: {GOLD};
                      text-decoration: none; font-weight: 700; font-size: 14px;
                      letter-spacing: 0.05em;">
                ⬅ 回上一頁
            </a>
            <a href="#"
               onclick="if (window.parent.goHomeTab) {{ window.parent.goHomeTab(); }} return false;"
               style="display: inline-block; padding: 10px 28px; background: {PANEL_LIGHT};
                      border: 1px solid {JADE}; border-radius: 6px; color: {JADE};
                      text-decoration: none; font-weight: 700; font-size: 14px;
                      letter-spacing: 0.05em;">
                🏠 返回首頁
            </a>
        </div>
        <p style="text-align: center; color: {MUTED}; font-size: 12px; margin-top: 6px;">
            點擊後會直接切換到對應分頁
        </p>
        """,
        unsafe_allow_html=True,
    )


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
    "<h1 style='white-space: nowrap;'>🖌️📜🏮 我的學習歷程：八週學習紀錄</h1>",
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
            <div class="seal-stamp"><span>學習</span></div>
            <h2 style="color: {TEXT}; margin: 0 0 8px 0;">我的學習歷程</h2>
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
        - **第二週** 目前已放入任務06、07、08、09
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

    back_to_home_button()

# ============================================================
# 第二週：任務06 + 任務07 + 任務08 + 任務09
# ============================================================
with tab_w2:
    st.markdown("<h2 style='white-space: nowrap;'>📦 第二週｜任務06：倉庫整理師</h2>", unsafe_allow_html=True)
    st.caption("儲位重排ABC＋服務藍圖洞察")
    st.markdown("適用：Week2・Day6　　預估填寫時間：60分鐘（14:45-15:45）")

    st.subheader("Section 1｜情境設定（5 min）")
    st.markdown(
        "**情境文字**：虛擬企業A：中型3PL物流商，主倉桃園，服務跨境電商客戶。\n"
        "- 倉庫規格：5列×10排＝50個儲位\n"
        "- SKU數：100個\n"
        "- 9月份出貨明細：SKU_出貨明細_202509.csv\n"
        "- 現況：儲位按字母順序排列（SKU001在1-1）\n\n"
        "**你的任務**：用ABC分類＋服務藍圖洞察，重新規劃儲位。"
    )

    st.subheader("Section 2｜觀念回顧（填空，8 min）")
    st.markdown("**2.1 ABC分類門檻**")
    abc_data = {
        "類別": ["A", "B", "C"],
        "累計出貨佔比": ["80%以下", "80%~95%", "95%以上"],
        "SKU比例（預期）": ["約20%", "約30%", "約50%"],
        "儲位策略": ["黃金區、最近、低層、補貨頻繁", "中央區、中高層", "外圍／高層／末端"],
    }
    st.table(pd.DataFrame(abc_data).set_index("類別"))

    st.markdown("**2.2 EIQ-PCB名詞填空**")
    eiq_data = {
        "字母": ["E", "I", "Q", "P", "C", "B"],
        "意義": ["E(Entry訂單)", "I(Item品項)", "Q(Quantity數量)", "棧板(Pallet)", "箱(Carton)", "盒(Box)"],
        "衡量什麼": ["訂單筆數", "不重複SKU數（商品廣度）", "數量", "棧板揀", "整箱揀", "散貨揀"],
    }
    st.table(pd.DataFrame(eiq_data).set_index("字母"))

    st.markdown("**2.3 反直覺回憶（連連看）**")
    counter_data = {
        "反直覺說法": ["1. 熱銷品不該都放最近", "2. ABC不是品項佔比", "3. 儲位是服務，不是工程"],
        "為什麼（答案）": [
            "B. 看IK（被點頻率）而不是IQ（總量）",
            "A. 出貨量佔比，不是品項數佔比",
            "C. 揀貨員的彎腰／安全／心理負荷也是成本",
        ],
    }
    st.table(pd.DataFrame(counter_data).set_index("反直覺說法"))

    st.subheader("Section 3｜Pandas實作（25 min）")
    st.markdown("**3.1 程式檢核點觀察**")
    st.code(
        'import pandas as pd\n\n'
        '# 步驟1：讀資料\n'
        'df = pd.read_csv("SKU_出貨明細_202509.csv", parse_dates=["訂單日期"])\n'
        'print(df.shape)   # 預期：約6,000列×5欄\n\n'
        '# 步驟2：聚合到SKU層\n'
        'sku = (df.groupby("SKU")\n'
        '        .agg(總出貨量=("數量", "sum"), 出貨筆數=("訂單編號", "nunique"))\n'
        '        .reset_index()\n'
        '        .sort_values("總出貨量", ascending=False))\n'
        'print(sku.head(10))\n\n'
        '# 步驟3：累計佔比＋ABC分類\n'
        'sku["累計佔比"] = sku["總出貨量"].cumsum() / sku["總出貨量"].sum()\n'
        'sku["類別"] = pd.cut(\n'
        '    sku["累計佔比"],\n'
        '    bins=[0, 0.80, 0.95, 1.0],\n'
        '    labels=["A", "B", "C"]\n'
        ')\n'
        'print(sku["類別"].value_counts())',
        language="python",
    )

    st.markdown("**3.2 結果填表**")
    result_data = {
        "類別": ["A", "B", "C", "合計"],
        "SKU數": [27, 35, 38, 100],
        "出貨量總和": ["46,246", "8,833", "2,931", "－"],
        "佔總出貨%": ["79.7%", "15.2%", "5.1%", "100%"],
    }
    st.table(pd.DataFrame(result_data).set_index("類別"))

    st.subheader("Section 4｜儲位重排（10 min）")
    st.markdown("**4.1 重排策略宣告（自選）**")
    st.markdown("- ☑ 動態熱區（A在中央黃金區／B在外圍中層／C在末端）")
    st.markdown("- ☐ 類別分區＋ABC（同類別內再分ABC）")
    st.markdown("- ☐ 自定策略")

    st.markdown("**4.2 儲位分配視覺化**")
    layout_data = {
        "類別": ["A", "B", "C"],
        "重排前": ["可能分散在各區，甚至離出口較遠", "與其他商品混放", "與熱門商品佔用相同位置"],
        "重排後": ["集中於靠近出口的黃金區，方便快速揀貨", "放置於外圍中層區域", "放置於末端或較遠儲位"],
    }
    st.table(pd.DataFrame(layout_data).set_index("類別"))

    st.success("✅ 4.3 預估改善：預估改善揀貨距離省 45.7%")

    st.subheader("Section 5｜服務洞察（7 min）")
    st.markdown("**5.1 選1個失效點（Pain Point）：痛點描述**")
    st.info(
        "揀貨員每天彎腰蹲下約200次拿取熱銷小量品項，因A類品項散落在各個高低儲位，"
        "長期恐造成腰部職業傷害，也拖慢揀貨速度。"
    )

    st.markdown("**5.2 ABC重排如何直接改善這個痛點？**")
    st.markdown(
        "重排後A類27個SKU全部集中在儲位C、D列（腰部90-150公分黃金高度）且靠近出口，"
        "揀貨員不再需要蹲低或墊腳取貨，單趟揀貨的彎腰動作預估減少約5成，且動線縮短45.7%。"
    )

    st.markdown("**5.3 一段話總結：儲位＝服務介面**")
    st.caption("提示：呼應今天金句「儲位不是工程問題，是服務承諾的兌現現場」")
    st.markdown(
        "儲位安排看似只是倉庫內部效率問題，實際上直接決定客戶「24小時到貨」承諾能否兌現。"
        "揀貨員找到SKU的速度，從客戶角度是服務體驗，從營運角度是揀貨工時；"
        "儲位規劃錯誤，最終會轉化成客戶不滿與員工職業傷害的雙重成本。"
    )

    st.subheader("Section 6｜反直覺收口三問（5 min）")
    reflect6_data = {
        "問題": [
            "如果今天的倉是「自動化AGV倉」，你的ABC分類還重要嗎？為什麼？",
            "如果今天賣的是「季節性服飾」，你的ABC分類有什麼陷阱？",
            "如果老闆說「下週要降30%倉儲面積」，你會先動A/B/C哪一類？為什麼？",
        ],
        "我的回答": [
            "重要，但角色會改變。在AGV（自動導引車）倉庫中，商品搬運主要由AGV完成，"
            "人員走動已不是主要成本，因此ABC分類不再只是縮短揀貨距離，而是用來優化AGV的"
            "行駛路線、補貨順序、儲位利用率等。",
            "ABC分類會受到時間影響，不能長期固定。例如冬季外套在冬天可能是A類商品，"
            "但到了夏天可能變成C類。如果一直沿用舊的ABC分類，可能會讓熱門商品放錯位置，"
            "降低揀貨效率。因此季節性商品需要定期重新分析與調整分類。",
            "我會先調整C類商品。因為C類商品出貨量最低、周轉率較低，較適合集中存放、"
            "提高儲位密度，甚至評估移至備用倉或降低庫存。A類商品仍應保留在黃金儲位，"
            "以維持揀貨效率與服務品質，避免影響出貨速度。",
        ],
    }
    st.table(pd.DataFrame(reflect6_data).set_index("問題"))

    # ---------- 任務07｜遲到偵探 ----------
    st.divider()
    st.markdown("<h2 style='white-space: nowrap;'>🕵️ 任務07｜遲到偵探</h2>", unsafe_allow_html=True)
    st.caption("OTD三層分析＋IQR異常偵測＋Folium地圖看板")
    st.markdown("適用：Week2・Day7　　預估110分鐘（14:00-15:50）")

    st.subheader("Section 1｜情境（5 min）")
    st.markdown(
        "虛擬企業B：中部4PL配送商，服務200家連鎖便利商店。\n"
        "- 9月配送紀錄：約6,000筆（配送紀錄_202509.csv）\n"
        "- 路線：R-01至R-09（共9條）\n"
        "- 司機：D-01至D-12（共12位）\n"
        "- 欄位：訂單編號、路線、司機、預計到達、實際到達、客戶時窗起/迄、貨損旗標、緯度/經度\n\n"
        "**老闆抱怨**：OTD變差，但不知道是路線爛、司機爛，還是訂單時段太密集。\n\n"
        "**你的任務**：用90分鐘給他答案。"
    )

    st.subheader("Section 2｜觀念回顧（填空，10 min）")
    st.markdown("**2.1 OTD三種口徑**")
    otd_data = {
        "口徑": ["嚴格OTD", "計畫OTD", "三方加權OTD"],
        "公式": ["準時送達訂單／全部訂單", "依排程準時訂單／已排程訂單", "時窗×完整×無損傷"],
        "適用情境": ["客戶視角（B2C高承諾）", "排程視角（內部KPI）", "製造業／醫藥"],
    }
    st.table(pd.DataFrame(otd_data).set_index("口徑"))

    st.markdown("**2.2 異常偵測三大武器**")
    weapon_data = {
        "武器": ["IQR", "Z-score", "Rolling滾動"],
        "適用情境": ["偏態分布（右偏）", "對稱／常態分布", "有趨勢／季節性資料"],
        "公式重點": ["下界＝Q1-1.5×IQR，上界＝Q3+1.5×IQR", "|Z|>2（或3）表示異常", "隨趨勢自動調整"],
    }
    st.table(pd.DataFrame(weapon_data).set_index("武器"))

    st.markdown("**2.3 反直覺三點**")
    counter7_data = {
        "反直覺點": ["OTD 100%不是好事", "異常是pattern不是點", "早到也是異常"],
        "為什麼": [
            "代表可能過度保守排程（時窗留太寬），反而犧牲了時效競爭力／成本效率",
            "單一個案可能只是意外，但重複出現的規律才代表系統性問題需要介入",
            "客戶依約定時窗規劃收貨人力，早到一樣打亂客戶端安排，等同失約",
        ],
    }
    st.table(pd.DataFrame(counter7_data).set_index("反直覺點"))

    st.subheader("Section 3｜Pandas三層OTD（20 min）")
    st.markdown("**3.1 整體OTD**")
    st.metric("整體嚴格OTD", "79.58%")

    st.markdown("**3.2 路線層OTD（最差5條）**")
    route_data = {
        "路線": ["R-03", "R-01", "R-05", "R-09", "R-02"],
        "OTD%": ["27.2%", "79.7%", "81.2%", "86.3%", "87.5%"],
        "訂單數": [662, 639, 672, 648, 654],
    }
    st.table(pd.DataFrame(route_data).set_index("路線"))

    st.markdown("**3.3 司機層OTD（最差5位）**")
    driver_data = {
        "司機": ["D-03", "D-07", "D-01", "D-04", "D-08"],
        "OTD%": ["35.7%", "48.9%", "84.8%", "86.2%", "86.9%"],
        "訂單數": [305, 832, 420, 442, 587],
    }
    st.table(pd.DataFrame(driver_data).set_index("司機"))

    st.markdown("**3.4 控制變量分析（關鍵）**")
    st.caption("問題：同一位司機跑不同路線，OTD是否一致？取最差司機D-03，看他在不同路線的OTD：")
    control_data = {
        "司機": ["D-03"],
        "路線": ["R-03"],
        "OTD%": ["35.7%"],
        "訂單數": [305],
    }
    st.table(pd.DataFrame(control_data).set_index("司機"))
    st.success("✅ 結論：這位司機是「只在某路線差」→ 主因：路線")

    st.subheader("Section 4｜異常偵測（20 min）")
    st.markdown("**4.1 武器選擇**")
    st.markdown(
        "☑ **IQR** — 因為：配送時間偏移分布經histogram檢視為右偏（skew=+1.08），"
        "IQR不受極端值影響，適合偏態分布"
    )

    st.markdown("**4.2 異常閾值**")
    st.code(
        'df["偏移分鐘"] = (df["實際到達"] - df["預計到達"]).dt.total_seconds() / 60\n'
        '# 用你選的方法計算閾值\n'
        'df["異常旗標"] = (df["偏移分鐘"] < 下界) | (df["偏移分鐘"] > 上界)',
        language="python",
    )
    st.info("異常筆數 ＝ 220 ／ 5,941（約3.7%）")

    st.markdown("**4.3 異常的pattern**")
    st.caption("異常訂單分布（用groupby看）：")
    pattern_data = {
        "維度": ["路線", "司機"],
        "Top1": ["R-03（211筆）", "D-07（152筆）"],
        "Top2": ["R-05（5筆）", "D-03（65筆）"],
        "Top3": ["R-01（2筆）", "D-05（1筆）"],
    }
    st.table(pd.DataFrame(pattern_data).set_index("維度"))

    st.subheader("Section 5｜Folium互動地圖（30 min）")
    st.markdown("**5.1 程式骨架**")
    st.code(
        'import folium\n'
        'm = folium.Map(location=[24.15, 120.65], zoom_start=11)\n'
        'for _, row in df.iterrows():\n'
        '    color = "red" if row["異常旗標"] else "green"\n'
        '    folium.CircleMarker(\n'
        '        location=[row["客戶緯度"], row["客戶經度"]],\n'
        '        radius=6,\n'
        '        color=color,\n'
        '        fill=True,\n'
        '        popup=f"訂單{row[\'訂單編號\']}<br>路線{row[\'路線代碼\']}"\n'
        '    ).add_to(m)\n'
        'm.save("OTD_地圖看板.html")',
        language="python",
    )

    st.markdown("**5.2 LayerControl路線篩選**")
    st.code(
        '# 把每條路線分到不同FeatureGroup\n'
        'for 路線 in df["路線代碼"].unique():\n'
        '    fg = folium.FeatureGroup(name=路線)\n'
        '    # ... 加marker ...\n'
        '    fg.add_to(m)\n'
        'folium.LayerControl().add_to(m)',
        language="python",
    )
    st.markdown("☐ 已成功加入路線篩選")

    st.subheader("Section 6｜病灶診斷（20 min）")
    st.markdown("**6.1 用一個句子定位主因**")
    st.markdown("主因是：☑ 路線　☐ 司機　☐ 時段　☐ 路線×時段交互　☐ 其他")

    st.markdown("**6.2 診斷報告（200字內）**")
    st.info(
        "整體嚴格OTD為79.58%，屬於警戒區間（低於90%）。異常筆數220筆（3.7%），"
        "高度集中在路線R-03（211筆，占異常總數96%）與司機D-07（152筆）。"
        "控制變量分析顯示：最差司機D-03的OTD在R-03路線為35.7%，排除R-03後，"
        "該司機在其他路線的OTD明顯回升，顯示問題主因是路線本身而非司機個人能力。"
        "建議行動是優先重新檢視R-03路線規劃，預期效益是OTD由27.2%提升至70%。"
    )

    st.markdown("**6.3 一條改善建議（一週內可動）**")
    action6_data = {
        "項目": ["行動", "責任人", "預期OTD改善"],
        "內容": ["重新檢視R-03路線規劃（距離／時窗／路線分配）", "排線主管", "由27.2%提升至70%"],
    }
    st.table(pd.DataFrame(action6_data).set_index("項目"))

    st.subheader("Section 7｜反直覺收口三問（5 min）")
    reflect7_data = {
        "問題": [
            "如果OTD是99.5%，你還用做這份分析嗎？為什麼？",
            "如果D-07 OTD偏低只在R-09，你會懲罰司機嗎？（Yes/No並說理由）",
            "如果老闆說「OTD<95%扣司機獎金」，可能引發什麼Goodhart's Law反效果？",
        ],
        "我的回答": [
            "要，因為要確認高分是否來自「排程刻意寬鬆」，而非真實效率",
            "No，因為問題出在路線非司機能力，懲罰治標不治本，還可能打擊士氣",
            "司機可能會虛報到達時間、或拒接困難路線的訂單，指標被操弄反而失真",
        ],
    }
    st.table(pd.DataFrame(reflect7_data).set_index("問題"))

    # ---------- 任務08｜供應鏈串接 ----------
    st.divider()
    st.markdown("<h2 style='white-space: nowrap;'>🔗 任務08｜供應鏈串接</h2>", unsafe_allow_html=True)
    st.caption("三表Merge＋主因標籤（個人作答）")
    st.markdown(
        "適用：Week2・Day8，預估填寫時間50分鐘（15:00-15:50）\n\n"
        "繳交方式：請依據指定方式繳交（/Day8/任務08_供應鏈串接/）\n\n"
        "建議檔名：D8_任務08_供應鏈串接_你的姓名（可打包zip或單檔）"
    )

    st.subheader("Section 1｜情境（3 min）")
    st.markdown(
        "虛擬企業C（食品批發商）的老闆抱怨：「最近C類庫存暴增30%，"
        "但業務說沒問題、倉儲說沒問題、採購也說沒問題。幫我抓出問題在誰。」\n\n"
        "**三表資料**：\n"
        "- purchase.csv（採購單號、SKU、供應商、訂購量、預計到貨）\n"
        "- receipt.csv（採購單號、SKU、實際到貨、實際數量、品質旗標）\n"
        "- sales.csv（銷售單號、SKU、客戶、出貨量、出貨日）\n\n"
        "**你的任務**：用Pandas Merge串起三表，找出Top5庫存積壓SKU，並標出主因。"
    )

    st.subheader("Section 2｜觀念回顧（填空，5 min）")
    st.markdown("**2.1 長鞭效應四大放大來源**")
    bullwhip_data = {
        "#": [1, 2, 3, 4],
        "來源": [
            "安全庫存效應(Safety Stock Amplification)", "批量訂購(Order Batching／EOQ)",
            "促銷與清庫存循環(Promotion Cycling)", "短缺博弈(Shortage Gaming)",
        ],
        "為什麼放大": ["看到大單就調高安全庫存", "訂滿經濟批量才下單", "促銷囤貨、平期清庫存", "怕拿不到就先報大量"],
    }
    st.table(pd.DataFrame(bullwhip_data).set_index("#"))

    st.markdown("**2.2 前置期三段拆解**")
    lt_data = {
        "段別": ["訂單前置", "供應商前置", "物流前置"],
        "縮寫": ["OLT", "SLT", "DLT"],
        "內容": ["內部從需求確認到下單", "供應商收單到出貨", "出貨到入庫"],
        "可控？": ["可控", "半控", "半控"],
    }
    st.table(pd.DataFrame(lt_data).set_index("段別"))

    st.markdown("**2.3 Pandas Merge四式—商業意義**")
    merge_data = {
        "寫法": ["inner", "left", "right", "outer"],
        "商業意義（用一句話）": [
            "只留A與B都有的資料（交集），用於嚴格分析，會漏看單邊獨有的異常",
            "保留A表全部，B對不到的填NaN，是「以A為主視角」的分析（例如看訂了但還沒到貨的採購單）",
            "保留B表全部，鏡像left，業界較少用（通常改成調換左右表位置、用left達成同樣效果）",
            "保留兩表全部資料，沒對到的都留著填NaN，用來看「哪裡缺漏」，適合稽核用途",
        ],
    }
    st.table(pd.DataFrame(merge_data).set_index("寫法"))

    st.markdown("**2.4 反直覺三點（連連看配對答案）**")
    match_data = {
        "配對": ["B", "A", "C"],
        "說法": [
            "真正成本：安全庫存×倉儲成本×資金利率",
            "看到C類庫存上升先看採購紀錄",
            "你選哪個how反映你選哪個視角",
        ],
    }
    st.table(pd.DataFrame(match_data).set_index("配對"))
    st.caption("原題：A. 庫存積壓很少是賣不好，常常是買得太兇　B. 供應商「便宜」常常用LT換來　C. Merge不是技術題，是商業假設題")

    st.subheader("Section 3｜三表Merge實作（15 min）")
    st.markdown("**3.1 Step 1：採購↔進貨（對LT）**")
    st.code(
        'import pandas as pd\n'
        'p = pd.read_csv("purchase.csv", encoding="utf-8-sig", parse_dates=["下單日", "預計到貨"])\n'
        'r = pd.read_csv("receipt.csv",  encoding="utf-8-sig", parse_dates=["實際到貨"])\n'
        '# 你選的how = "left"\n'
        'pr = p.merge(r, on=["採購單號", "SKU"], how="left")\n'
        '# LT三層\n'
        'pr["實際LT"]   = (pr["實際到貨"] - pr["下單日"]).dt.days\n'
        'pr["計畫LT"]   = (pr["預計到貨"] - pr["下單日"]).dt.days\n'
        'pr["LT延遲日"] = pr["實際LT"] - pr["計畫LT"]\n'
        'print(pr.head())',
        language="python",
    )
    st.markdown(
        "**你選的how＝\"left\"**\n\n"
        "**理由**：以採購單為主視角，保留「訂了但還沒到貨」的採購單，才能看出斷貨追責的早期警訊"
    )
    st.success("✅ 觀察：Merge後筆數＝102（原p＝102筆／原r＝73筆）")

    st.markdown("**3.2 Step 2：加銷售**")
    st.code(
        's = pd.read_csv("sales.csv", encoding="utf-8-sig", parse_dates=["出貨日"])\n'
        'sku_sales = s.groupby("SKU")["出貨量"].sum().reset_index()\n'
        'sku_sales.columns = ["SKU", "九月銷量"]\n'
        'full = pr.merge(sku_sales, on="SKU", how="left")\n'
        'full["九月銷量"] = full["九月銷量"].fillna(0)\n'
        'full["庫存積壓量"] = full["實際數量"] - full["九月銷量"]',
        language="python",
    )

    st.markdown("**3.3 Step 3：Top5積壓SKU**")
    st.code(
        '積壓 = full[full["庫存積壓量"] > 0].sort_values("庫存積壓量", ascending=False)\n'
        'print(積壓.head(5))',
        language="python",
    )
    top5_data = {
        "排名": [1, 2, 3, 4, 5],
        "SKU": ["S-1015", "S-1023", "S-1031", "S-1002", "S-1012"],
        "供應商": ["SUP-02", "SUP-03", "SUP-04", "SUP-02", "SUP-02"],
        "進貨量": [941, 438, 201, 580, 278],
        "9月銷量": [77, 135, 37, 418, 131],
        "積壓量": [864, 303, 164, 162, 147],
        "實際LT": ["11天", "28天", "16天", "12天", "14天"],
    }
    st.table(pd.DataFrame(top5_data).set_index("排名"))

    st.subheader("Section 4｜主因標籤（15 min）")
    st.caption("這是本任務最關鍵欄位，佔35分。")
    st.markdown("**4.1 主因四種候選**")
    reason_data = {
        "標籤": ["採購過量", "LT過長", "銷售下滑", "品質瑕疵"],
        "判定線索（程式實際）": [
            "實際進貨量>前三月平均月銷×倍率閾值（預設2.0）且庫存積壓量>100",
            "供應商LT變異（σ/μ）>0.30",
            "周轉率（九月銷量÷實際進貨量）<0.20",
            "不良次數≥1且不良率（不良次數÷實際進貨量）≥5%",
        ],
    }
    st.table(pd.DataFrame(reason_data).set_index("標籤"))

    st.markdown("**4.2 為Top5 SKU各標主因**")
    label5_data = {
        "SKU": ["S-1015", "S-1023", "S-1031", "S-1002", "S-1012"],
        "主因標籤": ["採購過量／銷售下滑", "採購過量／銷售下滑", "銷售下滑", "一般庫存", "採購過量"],
        "證據（具體數字）": [
            "進貨941件是前三月均銷91.7件的10.3倍（遠超2倍門檻）",
            "進貨438件是前三月均銷136.7件的3.2倍（超過2倍門檻）",
            "進貨201件其實只是前三月均銷290件的0.7倍（未達採購過量門檻）",
            "進貨580件是前三月均銷439.7件的1.3倍（未達2倍門檻）",
            "進貨278件是前三月均銷132件的2.1倍（略超2倍門檻）",
        ],
    }
    st.table(pd.DataFrame(label5_data).set_index("SKU"))

    st.markdown("**4.3 主因分布**")
    dist_data = {
        "主因": ["採購過量", "銷售下滑", "LT過長", "品質瑕疵（含退貨）"],
        "SKU數": ["3（S-1015、S-1023、S-1012）", "2（S-1015、S-1031）", "1（S-1023）", "0"],
    }
    st.table(pd.DataFrame(dist_data).set_index("主因"))
    st.success("✅ 結論：5個SKU中最常見主因是「採購過量」（3支SKU都有這個標籤：S-1015、S-1023、S-1012）")

    st.subheader("Section 5｜一句話結論（10 min）")
    st.info(
        "主因是採購過量，5支Top積壓SKU中3支進貨量遠超前三月平均銷量（S-1015達10.3倍）。"
        "我建議下月暫停這幾支SKU新採購，並要求業務重新核對9月銷售預測，"
        "同時對LT變異過高的供應商啟動改善計畫。"
    )

    st.subheader("Section 6｜GenAI sub-task 連動（2 min）")
    st.markdown("- 上午GenAI報告中，你抽到的新品＝ *（尚未填寫）*")
    st.markdown("- 回答：這份報告對你今天的任務08有沒有幫助？如何幫助？ *（尚未填寫）*")

    # ---------- 任務09｜決策簡報 ----------
    st.divider()
    st.markdown("<h2 style='white-space: nowrap;'>📢 任務09｜決策簡報</h2>", unsafe_allow_html=True)
    st.caption("SCQA＋金字塔＋風險三情境（個人作答，兩路徑擇一）")
    st.markdown(
        "適用：Week2・Day9，預估填寫時間110分鐘（14:00-15:50，含15分鐘Showtime）\n\n"
        "繳交方式：/Day9/任務09_決策簡報/，建議檔名 D9_任務09_決策簡報_你的姓名"
    )

    st.subheader("Section 1｜觀念回顧（填空，5 min）")
    st.markdown("**1.1 SCQA四字訣**")
    scqa_data = {
        "字母": ["S", "C", "Q", "A"],
        "完整字": ["Situation(現況)", "Complication(衝突)", "Question(問題)", "Answer(回答)"],
        "說明": ["當前情況（共識）", "變化/問題（衝突）", "引出的核心問題", "你的建議"],
    }
    st.table(pd.DataFrame(scqa_data).set_index("字母"))

    st.markdown("**1.2 金字塔原則三條原則**")
    st.markdown("- ☑ 主結論在頂端")
    st.markdown("- ☑ 三條支撐互斥（MECE）窮盡")
    st.markdown("- ☑ 數據／案例／證據放底層")

    st.markdown("**1.3 反直覺三點（自寫）**")
    d9_counter_data = {
        "問題": ["為什麼結論要先講？", "為什麼圖表愈多愈不專業？", "為什麼沒有風險評估老闆不買單？"],
        "我的答案": [
            "因為老闆時間有限，先講結論才能立刻判斷要不要繼續聽下去，業界匯報是結論先行，跟學界論文寫法相反",
            "圖越多代表你自己也還沒消化出重點，老闆會覺得你連自己都沒把握",
            "老闆怕的不是失敗方案，是沒被告知風險的方案，三情境寫齊反而讓老闆覺得你想清楚了",
        ],
    }
    st.table(pd.DataFrame(d9_counter_data).set_index("問題"))

    st.subheader("Section 2｜SCQA開場稿（15 min）")
    st.caption("寫成「老闆60秒能進入狀況」的開場。")
    scqa_script_data = {
        "字母": ["S（共識）", "C（衝突）", "Q（問題）", "A（建議）"],
        "你的句子（每段≤30字）": [
            "9月整體準時率79.6%，低於90%警戒線",
            "但R-03路線單獨看只有27.2%，拖累最嚴重",
            "該換司機、調路線，還是調時窗設定？",
            "建議重新規劃R-03路線排程",
        ],
    }
    st.table(pd.DataFrame(scqa_script_data).set_index("字母"))

    st.subheader("Section 3｜主結論句（關鍵，10 min）")
    st.markdown("一句話講完該做什麼，要有動詞、要有量化。")
    st.info("**主結論（50字內）**：「重新規劃R-03路線排程，1個月內觀察OTD能否回升至80%以上，預估月效益+8萬」")
    st.markdown("**自我檢核：**")
    st.markdown("- ☑ 第一個字是動詞（調整／重排／換約／強化…）")
    st.markdown("- ☑ 含具體量化（%／月／萬元）")
    st.markdown("- ☑ 30秒內能讓老闆做yes/no決定")

    st.subheader("Section 4｜三條MECE支撐（20 min）")
    mece_data = {
        "#": [1, 2, 3],
        "支撐句（≤30字）": ["問題真實存在", "主因可定位", "解法可行"],
        "證據（數字/圖表）": [
            "整體嚴格OTD僅79.6%，低於90%警戒線",
            "R-03的OTD僅27.2%，控制變量分析證實是路線問題非司機",
            "暫緩指派新司機至R-03，優先檢視距離／路況／時窗設定",
        ],
    }
    st.table(pd.DataFrame(mece_data).set_index("#"))
    st.markdown("**MECE自我檢查：**")
    st.markdown("- ☑ 三條互斥（沒有任何一條是另一條的子集）")
    st.markdown("- ☑ 三條窮盡（共同能撐住主結論）")

    st.subheader("Section 5｜一張關鍵圖（15 min）")
    st.markdown("不是三張，是一張。")
    keychart_data = {
        "項目": ["選擇的圖表類型", "為什麼是這張（50字內）", "截圖貼附位置（文字註記）"],
        "內容": [
            "箱型圖",
            "一次顯示中位數＋散布度，R-03整盒顯著低於95%目標線，其他路線基本貼線，"
            "比9條折線圖更省一頁，結論一眼看出。",
            "D6_D7_D8_D9整合版Tab4「關鍵圖」截圖，或D9單獨版故事B的箱型圖",
        ],
    }
    st.table(pd.DataFrame(keychart_data).set_index("項目"))

    st.subheader("Section 6｜風險三情境（關鍵，15 min）")
    risk_data = {
        "情境": ["樂觀", "悲觀", "不作為"],
        "預期結果": ["R-03路線OTD回升至80%以上", "路線問題非短期可解，僅小幅改善", "OTD持續低落，客訴增加"],
        "月效益（具體數字）": ["+8萬", "+3萬", "-5萬/月"],
        "對應行動": ["推進加速", "啟動Plan B", "（對照組）"],
    }
    st.table(pd.DataFrame(risk_data).set_index("情境"))

    st.subheader("Section 7｜Streamlit路徑 OR PPT路徑（20 min）")
    st.markdown("**選擇路徑（擇一）**：Streamlit")

    st.markdown("**路徑A：Streamlit**")
    st.markdown("- ☑ 主頁有 st.success 結論句　　☑ 三個 st.metric 卡片")
    st.markdown("- ☑ 一張 st.plotly_chart 主圖　　☑ st.expander 摺疊三條支撐")
    st.markdown("- ☑ 風險三情境表")
    st.caption("執行截圖貼附位置：D6_D7_D8_D9_整合版.py執行後Tab4選「故事B」的畫面截圖")

    st.markdown("**路徑B：PPT（Claude Cowork）**")
    st.markdown("- ☐ 標題列＋主結論　　☐ 三metric卡片")
    st.markdown("- ☐ 一張關鍵圖　　☐ 三條支撐")
    st.markdown("- ☐ 風險三情境　　☐ 主色#003366，字體層級分明")
    st.markdown("- PPT檔名：（未使用此路徑）")

    st.subheader("Section 8｜90秒Showtime腳本（5 min）")
    showtime_data = {
        "時段": ["0:00-0:30", "0:30-1:00", "1:00-1:30"],
        "內容": ["SCQA開場", "三條支撐", "風險三情境＋結語"],
    }
    st.table(pd.DataFrame(showtime_data).set_index("時段"))

    st.markdown("**逐字稿（可寫綱要）**")
    st.code(
        "0:00-0:30 SCQA開場\n"
        "「9月整體準時率79.6%，已經低於90%警戒線。但R-03這條路線單獨看只有27.2%，"
        "是全公司拖累最嚴重的一條。我們該換司機、調路線，還是重新檢視時窗設定？"
        "我建議重新規劃R-03路線排程。」\n\n"
        "0:30-1:00 三條支撐\n"
        "「第一，問題真的存在……第二，我知道問題在哪……是路線本身的問題，不是司機。"
        "第三，我知道怎麼解決——先別派新司機去，優先檢查距離、路況、時窗設定。」\n\n"
        "1:00-1:30 風險三情境＋結語\n"
        "「如果順利，每月多賺8萬；就算效果普通，還是能多賺3萬；"
        "如果什麼都不做，每月倒虧5萬。給我一個月觀察期，不達標我就回滾。」",
        language=None,
    )

    back_to_home_button()

with tab_w3:
    st.markdown("<h2>第三週</h2>", unsafe_allow_html=True)
    week_placeholder(3)
    back_to_home_button()

with tab_w4:
    st.markdown("<h2>第四週</h2>", unsafe_allow_html=True)
    week_placeholder(4)
    back_to_home_button()

with tab_w5:
    st.markdown("<h2>第五週</h2>", unsafe_allow_html=True)
    week_placeholder(5)
    back_to_home_button()

with tab_w6:
    st.markdown("<h2>第六週</h2>", unsafe_allow_html=True)
    week_placeholder(6)
    back_to_home_button()

with tab_w7:
    st.markdown("<h2>第七週</h2>", unsafe_allow_html=True)
    week_placeholder(7)
    back_to_home_button()

with tab_w8:
    st.markdown("<h2>第八週</h2>", unsafe_allow_html=True)
    week_placeholder(8)
    back_to_home_button()

st.divider()
st.caption("🌱 我的學習歷程：八週學習紀錄")
