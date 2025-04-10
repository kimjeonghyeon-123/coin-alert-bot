import json
import os
from datetime import datetime, timedelta

EVENT_LOG_FILE = "event_log.json"
LEARNED_IMPACTS_FILE = "learned_event_impacts.json"
LOOKBACK_HOURS = 6  # 이벤트 전후 분석 범위

def load_event_log():
    if not os.path.exists(EVENT_LOG_FILE):
        return []
    with open(EVENT_LOG_FILE, 'r') as f:
        return json.load(f)

def load_price_data(start_time, end_time):
    # price_logger의 로그를 불러와 해당 시간대의 가격변화 추출 (예: BTC_price_log.json)
    try:
        with open("BTC_price_log.json", 'r') as f:
            data = json.load(f)
        return [item for item in data if start_time <= item['timestamp'] <= end_time]
    except Exception as e:
        print(f"[ERROR] 가격 데이터 로드 실패: {e}")
        return []

def analyze_impact(event_time):
    start = event_time - timedelta(hours=LOOKBACK_HOURS)
    end = event_time + timedelta(hours=LOOKBACK_HOURS)
    prices = load_price_data(start.timestamp(), end.timestamp())
    
    if len(prices) < 2:
        return None

    pre_price = prices[0]['price']
    post_price = prices[-1]['price']
    movement = post_price - pre_price
    movement_pct = movement / pre_price * 100

    direction = "up" if movement > 0 else "down"
    duration = (prices[-1]['timestamp'] - prices[0]['timestamp']) / 3600

    return {
        "direction": direction,
        "magnitude_pct": round(abs(movement_pct), 2),
        "duration_hours": round(duration, 1)
    }

def learn_event_impacts():
    events = load_event_log()
    learned = {}

    for event in events:
        event_id = event['id']
        if event_id in learned:
            continue

        event_time = datetime.fromtimestamp(event['timestamp'])
        impact = analyze_impact(event_time)

        if impact:
            learned[event_id] = {
                "type": event['type'],
                "source": event.get('source', 'unknown'),
                "impact": impact
            }

    with open(LEARNED_IMPACTS_FILE, 'w') as f:
        json.dump(learned, f, indent=4)

    print(f"[학습 완료] 이벤트 영향 데이터 {len(learned)}개 저장됨.")

if __name__ == "__main__":
    learn_event_impacts()
