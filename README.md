# 🌱 我的自學歷程 Dashboard

一個用 Streamlit 打造的個人自學歷程紀錄工具，改編自「物流控制塔」多分頁儀表板架構。

## 功能分頁

| 分頁 | 內容 |
|---|---|
| 🏠 首頁總覽 | 四大追蹤面向的總覽卡片 |
| 📚 學習進度追蹤 | 各科目/單元完成度、投入時數 vs 進度散佈圖、待加強項目提醒 |
| 📝 學習日誌與心得反思 | 每日學習時數趨勢、科目時數佔比、心情篩選的心得紀錄 |
| 🎨 作品集/成果展示 | 專案、證書、作品的卡片式展示，可依類型/科目篩選 |
| 📋 給未來自己的成果報告 | 選一個科目，即時彙整並產出可下載的 Markdown 學習報告 |

## 檔案結構

```
self_study_dashboard/
├── app.py                       # 主程式
├── requirements.txt             # 套件需求
├── data/
│   ├── learning_progress.csv    # 學習進度資料（科目/單元/進度/時數/狀態）
│   ├── learning_journal.csv     # 學習日誌資料（日期/心情/時數/心得）
│   └── portfolio.csv            # 作品集資料（名稱/類型/科目/連結/說明）
└── README.md
```

## 如何客製化你自己的內容

直接編輯 `data/` 資料夾中的三個 CSV 檔案即可，不需要改程式碼：

- **learning_progress.csv**：新增你正在學的科目與單元，更新進度百分比、累計時數、狀態（未開始/進行中/已完成）
- **learning_journal.csv**：每次學習後新增一列，記錄日期、科目、時數、心情（emoji）、心得
- **portfolio.csv**：完成作品、拿到證書時新增一列，附上連結（沒有連結可留空）

## 本機執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 推上你自己的 GitHub Repo

```bash
# 在你的 repo 資料夾內，把這個資料夾內容複製進去（或直接用這個資料夾當 repo 根目錄）
git add .
git commit -m "建立自學歷程 Dashboard"
git push
```

## 部署到 Streamlit Community Cloud

1. 前往 [share.streamlit.io](https://share.streamlit.io)
2. 選擇你的 GitHub repo 與 `app.py` 作為進入點
3. 部署完成後即可得到公開網址（例如 `https://your-app-name.streamlit.app/`）
