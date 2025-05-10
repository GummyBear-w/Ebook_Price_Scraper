import pandas as pd
import plotly.express as px

df = pd.read_csv("book_prices.csv")
df["日期"] = pd.to_datetime(df["日期"])
df["價格"] = pd.to_numeric(df["價格"], errors="coerce")
df = df.dropna(subset=["價格", "ISBN"])

fig = px.line(
    df,
    x="日期",
    y="價格",
    color="書名",
    line_group="ISBN",
    hover_data=["作者", "ISBN", "連結"],
    title="📚 電子書價格追蹤"
)

fig.write_html("docs/price_plot.html")
