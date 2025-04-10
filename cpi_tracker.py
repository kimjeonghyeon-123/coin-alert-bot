import json
import os
import time
from datetime import datetime
from price_fetcher import get_current_price  # BTC 실시간 가격 불러오기

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

def analyze_cpi_reaction(cpi_time_str, duration_min=60):
    """CPI 발표 후 duration 분 동안의 비트코인 가격 변화를 분석"""
    price_log = load_json(BTC_PRICE_LOG)
    cpi_time = datetime.strptime(cpi_time_str, "%Y-%m-%d %H:%M:%S")

    prices = []
    for ts, price in price_log.items():
        t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        if cpi_time <= t <= cpi_time + timedelta(minutes=duration_min):
            prices.append((t, price))

    if not prices:
        print("📭 해당 시간대 가격 데이터 없음.")
        return

    start_price = prices[0][1]
    end_price = prices[-1][1]
    change_percent = ((end_price - start_price) / start_price) * 100

    print(f"📊 CPI 반응 분석: {duration_min}분 동안 {change_percent:.2f}% 변화")
    return change_percent

# 테스트용 수동 실행 예시
if __name__ == "__main__":
    # 수동 입력 테스트
    log_cpi_event(
        event_time="2025-04-10 12:30:00",
        expected_cpi=3.3,
        actual_cpi=3.7
    )

    # 반응 분석 (이전에 기록된 가격 로그가 있다고 가정)
    analyze_cpi_reaction("2025-04-10 12:30:00", duration_min=60)
