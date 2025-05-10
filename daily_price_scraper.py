from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import random
from datetime import datetime

def random_sleep(a=1.5, b=3.0):
    time.sleep(random.uniform(a, b))

def get_all_book_links(driver, wait, base_url):
    driver.get(base_url)
    book_links = []
    page_num = 1
    max_pages = 10  # 最多處理 10 頁

    current_url = driver.current_url
    while page_num <= max_pages:
        print(f"正在處理第 {page_num} 頁...")
        random_sleep(2, 4)

        books = driver.find_elements(By.CSS_SELECTOR, "div.book-card h2 a.cdk-link")
        for book in books:
            try:
                href = book.get_attribute("href")
                if href and href not in book_links:
                    book_links.append(href)
            except StaleElementReferenceException:
                continue

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button.control-button[aria-label="next page"]')
            if next_button.get_attribute("aria-disabled") == "true" or "disabled" in next_button.get_attribute("class"):
                print("✅ 已到最後一頁")
                break
            else:
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                random_sleep(0.8, 1.5)
                driver.execute_script("arguments[0].click();", next_button)
                random_sleep(2, 4)
    
                # ⛳️ 加入這段確認 URL 是否變動
                new_url = driver.current_url
                if new_url == current_url:
                    print("✅ 網址沒有變化，應是最後一頁")
                    break
                current_url = new_url
    
                page_num += 1
        except NoSuchElementException:
            print("❌ 找不到下一頁按鈕，結束")
            break

    return book_links

def extract_book_info(driver, wait, url):
    driver.get(url)
    try:
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item-info h1.title"))).text
    except:
        title = "無法取得書名"

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.pricing-figures")))
        random_sleep(1, 2)
        price_elem = driver.find_element(By.CSS_SELECTOR, "div.pricing-figures span.price")
        price_text = driver.execute_script("return arguments[0].textContent;", price_elem).strip()
        price = price_text.replace("NT$", "").replace(",", "").strip()
    except:
        price = "無法取得價格"

    try:
        isbn = "無法取得"
        lis = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.bookitem-secondary-metadata li")))
        for li in lis:
            if "書籍ID：" in li.text:
                isbn = li.text.replace("書籍ID：", "").strip()
                break
    except:
        isbn = "無法取得 ISBN"

    try:
        image_url = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.item-image img.cover-image"))).get_attribute("src")
    except:
        image_url = "無法取得圖片"

    return {
        "書名": title,
        "價格": price,
        "ISBN": isbn,
        "封面照片": image_url,
        "連結": url
    }

# 主流程
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

authors = {
    "卡繆": "https://www.kobo.com/tw/zh/search?query=%E5%8D%A1%E7%B9%86&ac=1&acp=%E5%8D%A1%E7%B9%86&ac.author=%E5%8D%A1%E7%B9%86&acpos=a2&uir=true&fclanguages=zh&fcsearchfield=author",
    "簡媜": "https://www.kobo.com/tw/zh/search?query=%E7%B0%A1%E5%AA%9C&ac=1&ac.morein=true&ac.author=%E7%B0%A1%E5%AA%9C&fcsearchfield=author&fclanguages=zh",
    "赫曼．赫塞": "https://www.kobo.com/tw/zh/search?query=%E8%B5%AB%E6%9B%BC%EF%BC%8E%E8%B5%AB%E5%A1%9E+&ac=1&ac.morein=true&ac.author=%E8%B5%AB%E6%9B%BC%EF%BC%8E%E8%B5%AB%E5%A1%9E+&fcsearchfield=author&fclanguages=zh"
}

csv_file = "book_prices.csv"
csv_headers = ["日期", "作者", "書名", "價格", "ISBN", "封面照片", "連結"]

if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()

today = datetime.now().strftime("%Y-%m-%d")

for author, url in authors.items():
    print(f"\n=== 處理作者：{author} ===")
    book_links = get_all_book_links(driver, wait, url)
    print(f"共取得 {len(book_links)} 筆連結")

    for idx, link in enumerate(book_links, 1):
        print(f"→ 第 {idx} 本書：{link}")
        info = extract_book_info(driver, wait, link)
        info["日期"] = today
        info["作者"] = author

        with open(csv_file, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writerow(info)

print("\n✅ 資料已儲存至 book_prices.csv")
driver.quit()
