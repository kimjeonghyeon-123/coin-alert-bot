import json
import os
import time
from datetime import datetime, timedelta
from price_fetcher import get_current_price
from learning_updater import update_learning_data_from_event
from event_impact_estimator import estimate_next_direction  # 다음 CPI 방향 예측

import requests

CPI_EVENT_LOG = "cpi_event_log.json"
BTC_PRICE_LOG = "btc_price_log.json"

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def fetch_latest_cpi():
    """
    CPI 예상치와 실제치 자동 수집 (tradingeconomics API 등 필요 시 API 연동)
    """
    try:
        response = requests.get("https://api.tradingeconomics.com/calendar/country/united-states?c=guest:guest")
        data = response.json()
        for event in data:
            if event["category"] == "CPI" and event["actual"]:
                return {
                    "time": event["date"],
                    "expected": float(event["forecast"]),
                    "actual": float(event["actual"])
                }
    except Exception as e:
        print("❌ CPI 데이터 수집 오류:", e)
    return None

def log_cpi_event(event_time, expected_cpi, actual_cpi):
    diff = actual_cpi - expected_cpi
    direction = "hot" if diff > 0 else "cool" if diff < 0 else "inline"
    entry_price = get_current_price()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log = load_json(CPI_EVENT_LOG)
    log[timestamp] = {
        "event_time": event_time,
        "expected_cpi": expected_cpi,
        "actual_cpi": actual_cpi,
        "diff": diff,
        "direction": direction,
        "btc_price_at_announcement": entry_price
    }
    save_json(CPI_EVENT_LOG, log)
    print(f"[✅ CPI 기록됨] 예상: {expected_cpi} / 실제: {actual_cpi} / BTC: {entry_price}")

    return direction, timestamp  # 분석 및 학습용 반환

def analyze_cpi_reaction(cpi_time_str, duration_min=60):
    price_log = load_json(BTC_PRICE_LOG)
    cpi_time = datetime.strptime(cpi_time_str, "%Y-%m-%d %H:%M:%S")

    prices = []
    for ts, price in price_log.items():
        t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        if cpi_time <= t <= cpi_time + timedelta(minutes=duration_min):
            prices.append((t, price))

    if not prices:
        print("📭 해당 시간대 가격 데이터 없음.")
        return None

    start_price = prices[0][1]
    end_price = prices[-1][1]
    change_percent = ((end_price - start_price) / start_price) * 100

    print(f"📊 CPI 반응 분석: {duration_min}분 동안 {change_percent:.2f}% 변화")
    return change_percent

def auto_process_cpi_event():
    cpi_data = fetch_latest_cpi()
    if not cpi_data:
        return

    event_time = cpi_data["time"]
    expected = cpi_data["expected"]
    actual = cpi_data["actual"]

    direction, ts = log_cpi_event(event_time, expected, actual)
    change = analyze_cpi_reaction(ts, duration_min=60)

    if change is not None:
        update_learning_data_from_event("CPI", direction, change)
        print("🧠 학습 반영 완료")

# 향후 CPI 예측 요청 시 호출
def predict_next_cpi_reaction():
    return estimate_next_direction("CPI")

