import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="我的自學歷程", layout="wide", page_icon="🖌️")
BASE = Path(__file__).parent / "data"

# ============================================================
# 設計代幣（Design Tokens）：古風配色 —— 墨黑底 × 朱紅印璽 × 泥金
# ============================================================
INK = "#130f0b"          # 頁面底色：墨黑（帶暖調，似漆器底）
PANEL = "#1d1710"         # 卡片/面板底色：深棕漆色
PANEL_LIGHT = "#2a2116"   # 卡片 hover 用的稍亮底色
BORDER = "#4a3b26"        # 邊框/分隔線：暗銅棕
JADE = "#c23b2c"          # 主色：朱紅（印璽紅，原變數名沿用，僅改色值）
TEAL = "#4a6b58"          # 次色：墨綠（松石入畫）
GOLD = "#c9a15a"          # 點綴色：泥金
RUST = "#8b6f47"          # 點綴色：赭石（古樸暖棕）
TEXT = "#f1e9d6"          # 主要文字：宣紙米白
MUTED = "#a08e6c"         # 次要/說明文字：舊金褪色調
PALETTE = [JADE, GOLD, TEAL, RUST, "#b23a2f", "#8a9a7e"]  # 多分類圖表用色序列

# ============================================================
# 全域 CSS：字體、卡片、分頁、指標、側邊欄、按鈕
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

/* 表格數字沿用楷體，但加寬字距讓數字更好辨識 */
[data-testid="stDataFrame"] * {{
    font-family: "cwTeXKai", serif !important;
    letter-spacing: 0.02em;
}}

/* 分頁列 */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid {BORDER};
}}
.stTabs [data-baseweb="tab"] {{
    color: {MUTED};
    font-weight: 500;
    padding: 10px 16px;
}}
.stTabs [aria-selected="true"] {{
    color: {JADE} !important;
    font-weight: 700;
    border-bottom: 2px solid {JADE} !important;
}}

/* 指標卡 st.metric */
[data-testid="stMetricValue"] {{
    color: {JADE};
    font-family: "cwTeXKai", serif;
}}
[data-testid="stMetricLabel"] {{
    color: {MUTED};
}}

/* 分隔線：加上居中雲紋裝飾，取代單調的橫線 */
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

/* 印璽角標（用於首頁橫幅） */
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

/* 側邊欄 */
[data-testid="stSidebar"] {{
    background-color: {PANEL};
    border-right: 1px solid {BORDER};
}}

/* 表格 */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    overflow: hidden;
}}

/* expander（心得反思卡片） */
[data-testid="stExpander"] {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
}}

/* 按鈕（下載報告、前往連結） */
.stDownloadButton button, .stLinkButton a {{
    background-color: {PANEL_LIGHT} !important;
    color: {JADE} !important;
    border: 1px solid {JADE} !important;
    border-radius: 6px !important;
}}
.stDownloadButton button:hover, .stLinkButton a:hover {{
    background-color: {JADE}22 !important;
}}

/* selectbox / radio 標籤 */
label {{
    color: {MUTED} !important;
}}

/* ============================================================
   響應式：手機（寬度 < 640px）
   - 楷體筆畫在小字號時辨識度下降，內文/表格自動切回黑體，標題保留楷體維持風格
   - 標題字級縮小，避免長標題在窄螢幕擠壓換行過密
   - 卡片高度改用最小高度，避免文字被裁切
   ============================================================ */
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
    """統一套用深色透明背景，讓圖表跟頁面底色融合，並套用楷體字型"""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT,
        font_family="cwTeXKai, serif",
        margin=dict(t=48, b=32, l=8, r=8),
    )
    return fig


st.markdown(
    "<h1 style='white-space: nowrap;'>🖌️📜🏮 我的自學歷程：進度追蹤 × 學習日誌 × 作品集</h1>",
    unsafe_allow_html=True,
)

tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 首頁總覽",
    "📚 學習進度追蹤",
    "📝 學習日誌與心得反思",
    "🎨 作品集/成果展示",
    "📋 給未來自己的成果報告",
])

# ============================================================
# 讀取資料
# ============================================================
@st.cache_data
def load_data():
    progress = pd.read_csv(BASE / "learning_progress.csv", encoding="utf-8-sig",
                            parse_dates=["更新日期"])
    journal = pd.read_csv(BASE / "learning_journal.csv", encoding="utf-8-sig",
                           parse_dates=["日期"])
    portfolio = pd.read_csv(BASE / "portfolio.csv", encoding="utf-8-sig",
                             parse_dates=["日期"])
    return progress, journal, portfolio

progress_file = BASE / "learning_progress.csv"
journal_file = BASE / "learning_journal.csv"
portfolio_file = BASE / "portfolio.csv"

data_ready = progress_file.exists() and journal_file.exists() and portfolio_file.exists()
if data_ready:
    df_progress, df_journal, df_portfolio = load_data()

# ============================================================
# Tab 0：首頁總覽
# ============================================================
with tab0:
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #241a0f 0%, {INK} 100%);
                    border: 1px solid {BORDER};
                    padding: 40px 30px; border-radius: 4px; margin-bottom: 24px;
                    position: relative; overflow: hidden;">
            <div class="seal-stamp"><span>自學</span></div>
            <h2 style="color: {TEXT}; margin: 0 0 8px 0;">我的自學歷程控制塔</h2>
            <p style="color: {MUTED}; margin: 0; font-size: 15px;">
                記錄每一次投入的時間、每一則反思，以及每一項完成的作品
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not data_ready:
        st.error("找不到 data 資料夾中的 CSV 檔案，請確認 learning_progress.csv / "
                  "learning_journal.csv / portfolio.csv 是否存在。")
    else:
        st.subheader("📊 四大追蹤面向")

        total_subjects = df_progress["科目"].nunique()
        avg_progress = df_progress["進度百分比"].mean()
        total_hours = df_progress["累計時數"].sum()
        total_entries = len(df_journal)
        total_works = len(df_portfolio)

        card_data = [
            {"icon": "📚", "title": "學習進度追蹤", "desc": f"{total_subjects} 個科目",
             "kpi": f"平均進度 {avg_progress:.0f}%", "color": JADE},
            {"icon": "📝", "title": "學習日誌與心得", "desc": f"{total_entries} 則紀錄",
             "kpi": f"累計時數 {total_hours:.0f} 小時", "color": TEAL},
            {"icon": "🎨", "title": "作品集/成果展示", "desc": f"{total_works} 項成果",
             "kpi": f"{df_portfolio['類型'].nunique()} 種類型", "color": GOLD},
            {"icon": "📋", "title": "給未來自己的報告", "desc": "階段性總結",
             "kpi": "可直接下載", "color": RUST},
        ]

        cols = st.columns(4)
        for col, card in zip(cols, card_data):
            with col:
                st.markdown(
                    f"""
                    <div style="background: {PANEL}; border: 1px solid {BORDER};
                                border-top: 4px solid {card['color']};
                                border-radius: 4px; padding: 18px; min-height: 170px;">
                        <div style="font-size: 28px;">{card['icon']}</div>
                        <div style="font-weight: 700; font-size: 16px; margin: 4px 0; color: {TEXT};">{card['title']}</div>
                        <div style="color: {MUTED}; font-size: 13px; margin-bottom: 12px;">{card['desc']}</div>
                        <div style="background: {card['color']}22; color: {card['color']};
                                    padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: 600;
                                    display: inline-block;">
                            {card['kpi']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.divider()
        st.subheader("🧭 使用導覽")
        st.markdown(
            """
            - **📚 學習進度追蹤** — 各科目/單元的完成度、投入時數與待加強項目
            - **📝 學習日誌與心得反思** — 每日學習時數趨勢、學習熱力圖、心情與心得紀錄
            - **🎨 作品集/成果展示** — 專案、證書、作業成果的整理與篩選
            - **📋 給未來自己的成果報告** — 選一個科目，產出一份可下載的階段性學習報告
            """
        )
        st.info("💡 點擊上方分頁按鈕切換各個追蹤面向；資料來源為 data/ 資料夾中的 CSV，可自行更新內容。")

# ============================================================
# Tab 1：學習進度追蹤
# ============================================================
with tab1:
    if not data_ready:
        st.error("找不到 learning_progress.csv")
    else:
        st.subheader("📚 各科目學習進度")

        c1, c2, c3, c4 = st.columns(4)
        completed = (df_progress["狀態"] == "已完成").sum()
        in_progress = (df_progress["狀態"] == "進行中").sum()
        c1.metric("追蹤科目數", f"{df_progress['科目'].nunique()} 個")
        c2.metric("已完成單元", f"{completed} 個")
        c3.metric("進行中單元", f"{in_progress} 個")
        c4.metric("累計學習時數", f"{df_progress['累計時數'].sum():.0f} 小時")

        st.divider()

        subj_summary = (df_progress.groupby("科目")
                         .agg(平均進度=("進度百分比", "mean"),
                              投入時數=("累計時數", "sum"),
                              單元數=("單元", "count"))
                         .reset_index().sort_values("平均進度", ascending=False))

        colA, colB = st.columns([1.2, 1])
        with colA:
            st.markdown("**各科目平均進度**")
            fig_bar = px.bar(subj_summary, x="科目", y="平均進度", color="平均進度",
                              color_continuous_scale=[PANEL_LIGHT, JADE], text="平均進度")
            fig_bar.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            fig_bar.update_layout(yaxis_range=[0, 110])
            st.plotly_chart(style_fig(fig_bar), width="stretch")
        with colB:
            st.markdown("**投入時數 vs 完成進度**")
            st.caption("右下角＝時數已投入不少、但進度仍低，是需要加強關注的科目")
            fig_scatter = px.scatter(subj_summary, x="投入時數", y="平均進度", color="科目",
                                      size="單元數", hover_data=["科目"],
                                      color_discrete_sequence=PALETTE)
            fig_scatter.add_hline(y=50, line_dash="dash", line_color=MUTED)
            st.plotly_chart(style_fig(fig_scatter), width="stretch")

        st.divider()
        st.subheader("🗂 單元明細")

        status_colors = {"已完成": f"background-color: {JADE}; color: #3a1608",
                          "進行中": f"background-color: {GOLD}; color: #2b1d05",
                          "未開始": f"background-color: {PANEL_LIGHT}; color: {MUTED}"}

        def color_status(val):
            return status_colors.get(val, "")

        show_cols = ["科目", "單元", "難度", "進度百分比", "累計時數", "狀態", "更新日期"]
        st.dataframe(
            df_progress[show_cols].sort_values(["科目", "更新日期"])
                .style.map(color_status, subset=["狀態"])
                .format({"更新日期": lambda d: d.strftime("%Y-%m-%d")}),
            width="stretch", hide_index=True,
        )

        needs_attention = subj_summary[subj_summary["平均進度"] < 50]
        if len(needs_attention):
            names = "、".join(needs_attention["科目"].tolist())
            st.warning(f"⚠️ 建議優先關注：**{names}**（平均進度低於 50%）")
        else:
            st.success("✅ 所有科目平均進度皆已過半，狀況良好！")

# ============================================================
# Tab 2：學習日誌與心得反思
# ============================================================
with tab2:
    if not data_ready:
        st.error("找不到 learning_journal.csv")
    else:
        st.subheader("📝 學習日誌總覽")

        df_journal = df_journal.sort_values("日期")
        streak_days = df_journal["日期"].dt.date.nunique()
        total_hours = df_journal["學習時數"].sum()
        avg_hours = df_journal["學習時數"].mean()
        this_month = df_journal[df_journal["日期"].dt.month == datetime.now().month]

        c1, c2, c3 = st.columns(3)
        c1.metric("累計紀錄天數", f"{streak_days} 天")
        c2.metric("累計學習時數", f"{total_hours:.1f} 小時")
        c3.metric("平均每次學習", f"{avg_hours:.1f} 小時")

        st.divider()

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown("**每日學習時數趨勢**")
            fig_trend = px.line(df_journal, x="日期", y="學習時數", markers=True,
                                 color_discrete_sequence=[JADE])
            fig_trend.add_hline(y=avg_hours, line_dash="dash", line_color=MUTED,
                                 annotation_text="平均")
            st.plotly_chart(style_fig(fig_trend), width="stretch")
        with r1c2:
            st.markdown("**各科目投入時數佔比**")
            subj_hours = df_journal.groupby("科目")["學習時數"].sum().reset_index()
            fig_pie = px.pie(subj_hours, names="科目", values="學習時數", hole=0.45,
                              color_discrete_sequence=PALETTE)
            st.plotly_chart(style_fig(fig_pie), width="stretch")

        st.divider()
        st.subheader("💬 心得反思紀錄")

        mood_options = ["全部"] + sorted(df_journal["心情"].unique().tolist())
        mood_filter = st.selectbox("依心情篩選", mood_options)
        view_journal = df_journal if mood_filter == "全部" else df_journal[df_journal["心情"] == mood_filter]

        for _, row in view_journal.sort_values("日期", ascending=False).iterrows():
            with st.expander(f"{row['日期'].strftime('%Y-%m-%d')} · {row['科目']} · {row['心情']}"):
                st.write(row["心得"])
                st.caption(f"當日學習時數：{row['學習時數']} 小時")

# ============================================================
# Tab 3：作品集/成果展示
# ============================================================
with tab3:
    if not data_ready:
        st.error("找不到 portfolio.csv")
    else:
        st.subheader("🎨 作品集與成果展示")

        type_icons = {"專案": "🛠", "作品": "🎨", "證書": "🏅"}

        c1, c2, c3 = st.columns(3)
        c1.metric("總成果數", f"{len(df_portfolio)} 項")
        c2.metric("涵蓋科目數", f"{df_portfolio['科目'].nunique()} 個")
        c3.metric("最新成果日期", df_portfolio["日期"].max().strftime("%Y-%m-%d"))

        st.sidebar.header("🎯 作品集篩選")
        type_options = ["(全部)"] + sorted(df_portfolio["類型"].unique().tolist())
        subj_options = ["(全部)"] + sorted(df_portfolio["科目"].unique().tolist())
        sel_type = st.sidebar.selectbox("類型", type_options)
        sel_subj = st.sidebar.selectbox("科目", subj_options)

        view = df_portfolio.copy()
        if sel_type != "(全部)":
            view = view[view["類型"] == sel_type]
        if sel_subj != "(全部)":
            view = view[view["科目"] == sel_subj]

        st.divider()

        if len(view) == 0:
            st.info("目前篩選條件下沒有成果，試試調整左側篩選器。")
        else:
            cols = st.columns(3)
            for i, (_, item) in enumerate(view.sort_values("日期", ascending=False).iterrows()):
                icon = type_icons.get(item["類型"], "📄")
                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div style="background: {PANEL}; border: 1px solid {BORDER};
                                    border-radius: 4px; padding: 16px;
                                    margin-bottom: 16px; min-height: 200px;">
                            <div style="font-size: 24px;">{icon}</div>
                            <div style="font-weight: 700; font-size: 15px; margin: 6px 0; color: {TEXT};">{item['名稱']}</div>
                            <div style="color: {MUTED}; font-size: 12px;">{item['科目']} · {item['日期'].strftime('%Y-%m-%d')}</div>
                            <div style="color: {TEXT}; opacity: 0.85; font-size: 13px; margin-top: 8px;">{item['說明']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if isinstance(item["連結"], str) and item["連結"].strip():
                        st.link_button("🔗 前往連結", item["連結"])

# ============================================================
# Tab 4：給未來自己的成果報告
# ============================================================
with tab4:
    st.markdown("<h2 style='white-space: nowrap;'>📋 給未來自己的成果報告</h2>", unsafe_allow_html=True)
    st.caption("選一個科目，即時彙整進度、日誌與作品集資料，產出一份階段性學習報告")

    if not data_ready:
        st.error("資料不齊全，無法產生報告")
    else:
        subj_list = sorted(df_progress["科目"].unique().tolist())
        chosen_subject = st.selectbox("選擇科目", subj_list)

        p_sub = df_progress[df_progress["科目"] == chosen_subject]
        j_sub = df_journal[df_journal["科目"] == chosen_subject]
        w_sub = df_portfolio[df_portfolio["科目"] == chosen_subject]

        avg_progress = p_sub["進度百分比"].mean()
        total_hours = p_sub["累計時數"].sum()
        completed_units = (p_sub["狀態"] == "已完成").sum()
        total_units = len(p_sub)
        journal_hours = j_sub["學習時數"].sum()

        st.success(f"📌 **{chosen_subject}** 目前平均進度 **{avg_progress:.0f}%**，"
                   f"已完成 {completed_units}/{total_units} 個單元，累計投入 {total_hours:.0f} 小時")

        kc1, kc2, kc3 = st.columns(3)
        kc1.metric("平均進度", f"{avg_progress:.0f}%")
        kc2.metric("累計時數", f"{total_hours:.0f} 小時")
        kc3.metric("相關作品/證書", f"{len(w_sub)} 項")

        st.divider()
        st.subheader("📌 三個重點回顧")
        st.markdown(f"- **投入狀況**：近期日誌中共記錄 {len(j_sub)} 次學習，累計 {journal_hours:.1f} 小時")
        if len(p_sub[p_sub['狀態'] != '已完成']):
            next_unit = p_sub[p_sub["狀態"] != "已完成"].sort_values("進度百分比").iloc[0]
            st.markdown(f"- **待加強單元**：「{next_unit['單元']}」目前進度 {next_unit['進度百分比']}%")
        else:
            st.markdown("- **待加強單元**：目前所有單元皆已完成！")
        if len(w_sub):
            latest_work = w_sub.sort_values("日期", ascending=False).iloc[0]
            st.markdown(f"- **最新成果**：{latest_work['名稱']}（{latest_work['日期'].strftime('%Y-%m-%d')}）")
        else:
            st.markdown("- **最新成果**：尚未在作品集中登錄此科目的成果")

        st.divider()
        st.subheader("📥 下載階段性學習報告")

        report_lines = [
            f"# {chosen_subject} 階段性學習報告",
            f"產生日期：{datetime.now().strftime('%Y-%m-%d')}", "",
            "## 現況摘要",
            f"- 平均進度：{avg_progress:.0f}%",
            f"- 已完成單元：{completed_units}/{total_units}",
            f"- 累計學習時數：{total_hours:.0f} 小時（日誌紀錄 {journal_hours:.1f} 小時）", "",
            "## 單元明細",
        ]
        for _, row in p_sub.iterrows():
            report_lines.append(f"- {row['單元']}（{row['難度']}）：{row['進度百分比']}% · {row['狀態']}")
        report_lines.append("")
        report_lines.append("## 學習心得摘錄")
        for _, row in j_sub.sort_values("日期").iterrows():
            report_lines.append(f"- {row['日期'].strftime('%Y-%m-%d')}（{row['心情']}）：{row['心得']}")
        report_lines.append("")
        report_lines.append("## 相關作品/成果")
        if len(w_sub):
            for _, row in w_sub.iterrows():
                report_lines.append(f"- {row['名稱']}（{row['類型']}，{row['日期'].strftime('%Y-%m-%d')}）：{row['說明']}")
        else:
            report_lines.append("- （尚無登錄成果）")
        report_lines += ["", "## 給未來自己的一句話",
                         "持續累積，每一次練習都會成為下一次突破的基礎。"]

        report_md = "\n".join(report_lines)
        st.code(report_md, language="markdown")
        st.download_button("📥 下載報告 (.md)", data=report_md,
                           file_name=f"{chosen_subject}_學習報告_{datetime.now().strftime('%Y%m%d')}.md",
                           mime="text/markdown")

st.divider()
st.caption("🌱 我的自學歷程：學習進度追蹤 × 學習日誌與心得反思 × 作品集/成果展示 × 階段性成果報告")
