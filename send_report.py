import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# 檔案名稱
csv_file = "book_prices.csv"

# 載入資料
df = pd.read_csv(csv_file)
df["日期"] = pd.to_datetime(df["日期"], format="%Y-%m-%d")

# 取得今天與昨天的日期
today = datetime.now().date()
yesterday = today - timedelta(days=1)

# 篩選今天與昨天的資料
today_df = df[df["日期"] == pd.Timestamp(today)]
yesterday_df = df[df["日期"] == pd.Timestamp(yesterday)]

# 對照價格變動（用 ISBN 當主鍵）
today_prices = today_df.set_index("ISBN")["價格"]
yesterday_prices = yesterday_df.set_index("ISBN")["價格"]

up, down, unchanged = [], [], []

for isbn, today_price in today_prices.items():
    try:
        y_price = float(yesterday_prices[isbn])
        t_price = float(today_price)

        if t_price > y_price:
            up.append((isbn, t_price, y_price))
        elif t_price < y_price:
            down.append((isbn, t_price, y_price))
        else:
            unchanged.append((isbn, t_price))
    except:
        continue

# Email 設定
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
TO_EMAIL = EMAIL_ADDRESS  # 自己寄給自己

msg = MIMEMultipart("alternative")
msg["Subject"] = f"每日 Kobo 價格報告：{today.strftime('%Y-%m-%d')}"
msg["From"] = EMAIL_ADDRESS
msg["To"] = TO_EMAIL

body = f"""
📚 Kobo 書籍價格報告（{today.strftime('%Y-%m-%d')})

共比對 {len(today_prices)} 本書：
- 📈 上漲：{len(up)} 本
- 📉 下跌：{len(down)} 本
- ➖ 無變化：{len(unchanged)} 本

"""

if up:
    body += "\n📈 上漲書籍：\n"
    for isbn, t, y in up:
        title = df[df["ISBN"] == isbn]["書名"].iloc[-1]
        body += f"- {title}（{y} → {t}）\n"

if down:
    body += "\n📉 下跌書籍：\n"
    for isbn, t, y in down:
        title = df[df["ISBN"] == isbn]["書名"].iloc[-1]
        body += f"- {title}（{y} → {t}）\n"

if not up and not down:
    body += "\n📪 所有書籍價格皆未變動。\n"

msg.attach(MIMEText(body, "plain"))

# 發信
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    print("✅ Email 已成功發送。")
except Exception as e:
    print("❌ 發送 Email 失敗：", str(e))
