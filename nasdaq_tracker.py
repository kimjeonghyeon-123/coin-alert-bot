# nasdaq_tracker.py

import yfinance as yf
import time
import json
import os
from datetime import datetime, timedelta
from price_fetcher import get_current_price
from learning_updater import update_learning_data_from_event
from notifier import send_telegram_message

NASDAQ_SYMBOL = "^IXIC"
EVENT_LOG_PATH = "nasdaq_event_log.json"
BTC_PRICE_LOG = "btc_price_log.json"

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def fetch_recent_nasdaq():
    ticker = yf.Ticker(NASDAQ_SYMBOL)
    df = ticker.history(period="10m", interval="1m")
    if df.empty:
        return []
    return df["Close"].tolist()

def detect_nasdaq_event(prices, threshold_percent=0.7):
    if len(prices) < 5:
        return False, 0.0

    start_price = prices[0]
    end_price = prices[-1]
    change_percent = ((end_price - start_price) / start_price) * 100

    if abs(change_percent) >= threshold_percent:
        return True, change_percent
    return False, change_percent

def log_nasdaq_event(change_percent):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    direction = "up" if change_percent > 0 else "down"
    btc_price = get_current_price()

    log = load_json(EVENT_LOG_PATH)
    log[timestamp] = {
        "direction": direction,
        "nasdaq_change_percent": change_percent,
        "btc_price_at_event": btc_price
    }
    save_json(EVENT_LOG_PATH, log)

    print(f"[📈 나스닥 이벤트 기록됨] {direction.upper()} {change_percent:.2f}% / BTC: {btc_price}")
    send_telegram_message(f"📈 [나스닥 이벤트] 방향: {direction.upper()} / 변동률: {change_percent:.2f}%\nBTC: {btc_price}")

    return timestamp, direction

def analyze_btc_reaction_to_nasdaq_event(event_time_str, duration_min=60):
    price_log = load_json(BTC_PRICE_LOG)
    event_time = datetime.strptime(event_time_str, "%Y-%m-%d %H:%M:%S")

    prices = []
    for ts, price in price_log.items():
        t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        if event_time <= t <= event_time + timedelta(minutes=duration_min):
            prices.append((t, price))

    if not prices:
        print("📭 해당 시간대 BTC 가격 데이터 없음.")
        return None

    start_price = prices[0][1]
    end_price = prices[-1][1]
    change_percent = ((end_price - start_price) / start_price) * 100

    print(f"📊 BTC 반응 분석: {duration_min}분 동안 {change_percent:.2f}% 변화")
    
    # 로그에도 반영
    log = load_json(EVENT_LOG_PATH)
    if event_time_str in log:
        log[event_time_str]["btc_change_percent"] = change_percent
        save_json(EVENT_LOG_PATH, log)

    return change_percent

def auto_monitor_nasdaq():
    prices = fetch_recent_nasdaq()
    if not prices:
        print("❌ 나스닥 데이터 없음")
        return

    event_detected, change = detect_nasdaq_event(prices)
    if event_detected:
        ts, direction = log_nasdaq_event(change)
        btc_reaction = analyze_btc_reaction_to_nasdaq_event(ts)
        if btc_reaction is not None:
            update_learning_data_from_event("NASDAQ", direction, btc_reaction)
            print("🧠 학습 반영 완료")
