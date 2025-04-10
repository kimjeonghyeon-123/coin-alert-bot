# nasdaq_tracker.py

import json
import os
from datetime import datetime, timedelta
from price_fetcher import get_current_price
from learning_updater import update_learning_data_from_event
from notifier import send_telegram_message

NASDAQ_LOG = "nasdaq_price_log.json"
NASDAQ_EVENT_LOG = "nasdaq_event_log.json"

PERCENT_THRESHOLD = 0.7  # 5분간 ±0.7% 이상일 때 이벤트로 간주
DURATION_MINUTES = 5

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def detect_nasdaq_spike():
    log = load_json(NASDAQ_LOG)

    if not log:
        print("❌ 나스닥 로그 없음")
        return

    sorted_entries = sorted(log.items(), key=lambda x: x[0])
    latest_time = datetime.strptime(sorted_entries[-1][0], "%Y-%m-%d %H:%M:%S")
    window_start = latest_time - timedelta(minutes=DURATION_MINUTES)

    prices = [
        (datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"), price)
        for ts, price in sorted_entries
        if window_start <= datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") <= latest_time
    ]

    if len(prices) < 2:
        print("📭 가격 변화 감지 불가 (데이터 부족)")
        return

    start_price = prices[0][1]
    end_price = prices[-1][1]
    change_pct = ((end_price - start_price) / start_price) * 100

    if abs(change_pct) >= PERCENT_THRESHOLD:
        direction = "spike_up" if change_pct > 0 else "spike_down"
        timestamp = latest_time.strftime("%Y-%m-%d %H:%M:%S")
        btc_price = get_current_price()

        # 이벤트 기록
        event_log = load_json(NASDAQ_EVENT_LOG)
        event_log[timestamp] = {
            "start_price": start_price,
            "end_price": end_price,
            "change_pct": change_pct,
            "direction": direction,
            "btc_price_at_event": btc_price
        }
        save_json(NASDAQ_EVENT_LOG, event_log)

        # 학습 반영
        update_learning_data_from_event("NASDAQ", direction, change_pct)

        # 텔레그램 알림
        send_telegram_message(f"📉 NASDAQ {direction} 감지 ({change_pct:.2f}%)\nBTC: {btc_price}")

        print(f"✅ 이벤트 기록됨 - {direction}, {change_pct:.2f}%")
    else:
        print(f"🟡 변화 미미: {change_pct:.2f}%")

def run_nasdaq_event_monitor():
    print("🚦 나스닥 이벤트 모니터링 시작")
    while True:
        detect_nasdaq_spike()
        time.sleep(60)

