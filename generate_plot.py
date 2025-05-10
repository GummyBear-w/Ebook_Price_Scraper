import pandas as pd
import plotly.express as px
import os

# 讀取資料
csv_file = "book_prices.csv"
df = pd.read_csv(csv_file)
df["日期"] = pd.to_datetime(df["日期"])
df["價格"] = pd.to_numeric(df["價格"], errors="coerce")
df = df.dropna(subset=["價格", "ISBN"])

# 確保 docs 資料夾存在
os.makedirs("docs", exist_ok=True)

# 各本書生成價格折線圖
isbn_to_plot_path = {}
for isbn, group in df.groupby("ISBN"):
    if group.shape[0] < 2:
        continue  # 只有一天資料不用畫圖
    fig = px.line(
        group,
        x="日期",
        y="價格",
        color="書名",
        line_group="ISBN",
        hover_data=["作者", "連結"],
        title=group["書名"].iloc[0]
    )
    plot_path = f"plot_{isbn}.html"
    fig.write_html(f"docs/{plot_path}", include_plotlyjs="cdn", full_html=False)
    isbn_to_plot_path[isbn] = plot_path

# 得到最新日期以用於每本書最新價格
latest_date = df["日期"].max()
latest_df = df[df["日期"] == latest_date]

# 各 ISBN 最低價格
min_price = df.groupby("ISBN")["價格"].min()

# 以作者分群
authors = ["全部作者"] + sorted(df["作者"].unique())

# 生成 index.html
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write("""
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>📄 電子書價格跟蹤</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
    <h1 class="mb-4">📄 電子書價格跟蹤</h1>
    <div class="mb-4">
        <label for="authorSelect" class="form-label">下拉式選單 選擇作者：</label>
        <select class="form-select" id="authorSelect" onchange="filterByAuthor()">
""")
    for author in authors:
        value = author if author != "全部作者" else "all"
        f.write(f'<option value="{value}">{author}</option>\n')
    f.write("""
        </select>
    </div>
    <div id="bookCards">
""")
    for _, row in latest_df.iterrows():
        isbn = row["ISBN"]
        image = row["封面照片"]
        title = row["書名"]
        price = row["價格"]
        link = row["連結"]
        author = row["作者"]
        min_p = min_price.get(isbn, price)
        chart_html = f'<iframe src="{isbn_to_plot_path.get(isbn, "")}" width="100%" height="300"></iframe>' if isbn in isbn_to_plot_path else '<p class="text-muted">目前無歷史價格資料</p>'
        f.write(f"""
<div class="card mb-4" data-author="{author}">
  <div class="row g-0">
    <div class="col-md-2">
      <img src="{image}" class="img-fluid rounded-start" alt="封面" style="height: 180px; object-fit: cover;">
    </div>
    <div class="col-md-10">
      <div class="card-body">
        <h5 class="card-title"><a href="{link}" target="_blank">{title}</a></h5>
        <p class="card-text">本日價格：NT${price}　歷史低價：NT${min_p}</p>
        {chart_html}
      </div>
    </div>
  </div>
</div>
""")
    f.write("""
    </div>
</div>
<script>
function filterByAuthor() {
    const selected = document.getElementById("authorSelect").value;
    document.querySelectorAll("#bookCards .card").forEach(card => {
        card.style.display = (selected === "all" || card.dataset.author === selected) ? "" : "none";
    });
}
</script>
</body>
</html>
""")
