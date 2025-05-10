import pandas as pd
import plotly.express as px
import os
from collections import defaultdict

# 建立資料夾
os.makedirs("docs", exist_ok=True)

# 讀取資料
df = pd.read_csv("book_prices.csv")
df["日期"] = pd.to_datetime(df["日期"])
df["價格"] = pd.to_numeric(df["價格"], errors="coerce")
df = df.dropna(subset=["價格", "ISBN"])

# 每本書最新價格 & 歷史最低價
latest_price = df.sort_values("日期").groupby("ISBN").last()["價格"]
lowest_price = df.groupby("ISBN")["價格"].min()

# 書本資訊
book_info = df.groupby("ISBN").last()[["書名", "封面照片", "作者", "連結"]]
book_info["最新價格"] = latest_price
book_info["歷史低價"] = lowest_price

# 用來產出 HTML 清單
html_blocks = []
author_to_isbns = defaultdict(list)

for isbn, row in book_info.iterrows():
    book_df = df[df["ISBN"] == isbn]

    # 產圖
    fig = px.line(
        book_df,
        x="日期",
        y="價格",
        title=row["書名"],
        markers=True
    )
    chart_path = f"docs/plot_{isbn}.html"
    fig.write_html(chart_path, include_plotlyjs=False, full_html=False)

    # 收集作者選單資訊
    author_to_isbns[row["作者"]].append(isbn)

    # HTML 區塊
    block = f"""
    <div class="book-block" data-author="{row['作者']}">
        <img src="{row['封面照片']}" alt="封面" class="cover">
        <div class="info">
            <h3><a href="{row['連結']}" target="_blank">{row['書名']}</a></h3>
            <p>本日價格：NT$ {row['最新價格']}　歷史低價：NT$ {row['歷史低價']}</p>
            <iframe src="plot_{isbn}.html" class="chart-frame"></iframe>
        </div>
    </div>
    """
    html_blocks.append(block)

# 作者選單
dropdown = '<select id="authorFilter"><option value="all">全部作者</option>'
for author in sorted(author_to_isbns.keys()):
    dropdown += f'<option value="{author}">{author}</option>'
dropdown += '</select>'

# HTML 頁面
html_template = f"""
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>📚 電子書價格追蹤</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: sans-serif;
            margin: 2em;
            background: #f5f5f5;
        }}
        h1 {{
            margin-bottom: 0.5em;
        }}
        select {{
            font-size: 1em;
            padding: 0.3em;
            margin-bottom: 1.5em;
        }}
        .book-block {{
            display: flex;
            gap: 1em;
            margin-bottom: 3em;
            padding: 1em;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .cover {{
            width: 160px;
            height: auto;
            border-radius: 4px;
        }}
        .info {{
            flex: 1;
        }}
        .chart-frame {{
            width: 100%;
            height: 320px;
            border: none;
        }}
    </style>
</head>
<body>
    <h1>📚 電子書價格追蹤</h1>
    <label>下拉式選單 選擇作者：</label>{dropdown}
    <div id="books">
        {''.join(html_blocks)}
    </div>

    <script>
        const selector = document.getElementById("authorFilter");
        selector.addEventListener("change", function() {{
            const selected = this.value;
            document.querySelectorAll(".book-block").forEach(block => {{
                if (selected === "all" || block.dataset.author === selected) {{
                    block.style.display = "flex";
                }} else {{
                    block.style.display = "none";
                }}
            }});
        }});
    </script>
</body>
</html>
"""

# 輸出主頁
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
