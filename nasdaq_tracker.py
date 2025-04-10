# nasdaq_tracker.py

import yfinance as yf
import json
import os
from datetime import datetime, timedelta
from price_fetcher import get_current_price
from learning_updater import update_learning_data_from_event

NASDAQ_LOG = "nasdaq_event_log.json"
BTC_LOG = "btc_price_log.json"
SYMBOL = "^IXIC"  # Nasdaq 100 Index (yfinance 코드)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def fetch_nasdaq_price():
    try:
        ticker = yf.Ticker(SYMBOL)
        hist = ticker.history(period="5m", interval="1m")
        if not hist.empty:
            latest = hist.iloc[-1]
            return float(latest["Close"]), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("❌ 나스닥 가격 수집 오류:", e)
    return None, None

def detect_nasdaq_event(threshold_percent=0.7, window_min=5):
    try:
        ticker = yf.Ticker(SYMBOL)
        hist = ticker.history(period=f"{window_min+1}m", interval="1m")
        if len(hist) < window_min:
            return None
        
        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        change = ((end_price - start_price) / start_price) * 100

        if abs(change) >= threshold_percent:
            return {
                "start_price": round(start_price, 2),
                "end_price": round(end_price, 2),
                "change_percent": round(change, 2),
                "event_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "direction": "up" if change > 0 else "down"
            }
    except Exception as e:
        print("❌ 나스닥 이벤트 감지 오류:", e)
    return None

def log_nasdaq_event(event):
    log = load_json(NASDAQ_LOG)
    btc_price = get_current_price()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log[timestamp] = {
        **event,
        "btc_price_at_event": btc_price
    }
    save_json(NASDAQ_LOG, log)
    print(f"📈 [나스닥 이벤트 기록] {event['direction']} {event['change_percent']}% / BTC: {btc_price}")
    return timestamp, event["direction"]

def analyze_btc_reaction(event_time_str, duration_min=60):
    btc_log = load_json(BTC_LOG)
    event_time = datetime.strptime(event_time_str, "%Y-%m-%d %H:%M:%S")

    prices = []
    for ts, price in btc_log.items():
        t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        if event_time <= t <= event_time + timedelta(minutes=duration_min):
            prices.append((t, price))

    if not prices:
        print("📭 BTC 반응 데이터 없음")
        return None

    start_price = prices[0][1]
    end_price = prices[-1][1]
    change = ((end_price - start_price) / start_price) * 100
    print(f"📊 BTC {duration_min}분 반응: {change:.2f}%")
    return change

def auto_monitor_nasdaq():
    event = detect_nasdaq_event()
    if event:
        ts, direction = log_nasdaq_event(event)
        btc_change = analyze_btc_reaction(ts, duration_min=60)
        if btc_change is not None:
            update_learning_data_from_event("NASDAQ", direction, btc_change)
            print("🧠 나스닥 이벤트 학습 반영 완료")
