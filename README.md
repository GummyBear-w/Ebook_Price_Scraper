# Ebook_Price_Scraper

本專案旨在每日自動爬取 Kobo 電子書平台上特定作者書籍的價格資訊，並透過 GitHub Actions 進行排程與更新，最終以可視化頁面展示價格波動與最低價紀錄，協助掌握價格趨勢與購買時機。（Kobo其實有提供api但僅限日本商店使用QQ）

## 專案簡介

本專案包含三個主要功能模組：

1. **自動爬蟲 (`daily_price_scraper.py`)**
   - 使用 Selenium 模擬使用者瀏覽行為以繞過網站的反爬蟲機制。
   - 每日自動訪問 Kobo 電子書搜尋頁面，擷取指定作者的所有書籍資料，包括：書名、價格、ISBN、封面圖片、連結等資訊。
   - 所有資料以 `book_prices.csv` 累積保存，具備追蹤歷史價格變化的能力。

2. **報告通知 (`send_report.py`)**
   - 每日比對最新價格與昨日價格，若有變化則記錄上下漲項目，否則顯示「都沒變」。
   - 將結果寄送至指定 Email，提醒使用者關注價格異動。
   - <img src="https://github.com/GummyBear-w/Ebook_Price_Scraper/raw/main/email_report.png" width = "100%">

3. **視覺化介面產生 (`generate_plot.py`)**
   - 使用 `pandas` 與 `plotly.express` 產生每本書的歷史價格折線圖。
   - 將視覺化結果以 HTML 格式嵌入網頁，並自動產生 `docs/index.html` 作為總覽介面。
   - 頁面內容可至本文件最下方預覽

## 技術架構

- **資料擷取**：`Selenium` + `ChromeDriver`
- **資料儲存**：CSV 累積格式（含歷史記錄）
- **自動排程與執行**：GitHub Actions（每天固定時間觸發）
- **視覺化呈現**：`plotly` + `HTML` + `Bootstrap`
- **靜態網頁託管**：GitHub Pages

## 專案檔案說明

| 檔案 / 資料夾         | 功能說明 |
|----------------------|----------|
| `daily_price_scraper.py`          | 每日自動爬取 Kobo 書籍價格與資訊，儲存至 `book_prices.csv`。 |
| `send_report.py`     | 比對前一日與當日價格，產出變動報告並寄送 Email 通知。 |
| `generate_plot.py`   | 根據歷史價格資料產生視覺化圖表與 HTML 展示頁面。 |
| `book_prices.csv`    | 儲存所有每日爬取的書籍價格資訊。 |
| `docs/`              | GitHub Pages 網頁根目錄，內含自動產生的 `index.html` 與折線圖檔案。 |
| `.github/workflows/` | 包含三個 GitHub Action 工作流程，用於每日排程執行爬蟲、寄信、產生視覺化。 |

## 觀看視覺化價格追蹤頁面

<img src="https://github.com/GummyBear-w/Ebook_Price_Scraper/raw/main/demo.gif" width="90%">

有興趣的話可以透過下列連結開啟每日更新的視覺化頁面（由 GitHub Pages 自動生成）：  
[價格追蹤頁面](https://gummybear-w.github.io/Ebook_Price_Scraper/)

頁面中可依作者篩選、瀏覽封面、點擊連結查看書籍頁面，並觀察每本書的價格變化趨勢。

---

