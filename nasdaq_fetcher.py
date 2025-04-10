# nasdaq_fetcher.py
import yfinance as yf
import time
import json
from datetime import datetime

NASDAQ_LOG = "nasdaq_price_log.json"

def get_nasdaq_price():
    ticker = yf.Ticker("^IXIC")  # NASDAQ Composite Index
    data = ticker.history(period="1d", interval="1m")
    if not data.empty:
        return float(data["Close"].iloc[-1])
    return None

def load_log():
    try:
        with open(NASDAQ_LOG, "r") as f:
            return json.load(f)
    except:
        return {}

def save_log(log):
    with open(NASDAQ_LOG, "w") as f:
        json.dump(log, f, indent=2)

def run_nasdaq_logger():
    print("📡 나스닥 가격 로깅 시작...")
    while True:
        price = get_nasdaq_price()
        if price:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            log = load_log()
            log[now] = price
            save_log(log)
            print(f"[🟢] {now} - NASDAQ: {price}")
        else:
            print("❌ 가격 불러오기 실패")
        time.sleep(60)  # 1분 간격
