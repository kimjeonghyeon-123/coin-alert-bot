import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

EVENT_LOG_FILE = "event_log.json"
PRICE_LOG_FILE = "price_history.json"
EVENT_LEARNING_FILE = "event_learning.json"

MIN_DATA_POINTS = 5


def load_json(path):
    if not os.path.exists(path):
        return [] if path.endswith('.json') else {}
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def find_price_change(prices, event_time):
    """
    가격 로그에서 이벤트 발생 후 최대 변화 비율과 지속 시간을 찾는다.
    """
    event_dt = datetime.fromisoformat(event_time)
    start_time = event_dt
    end_time = event_dt + timedelta(hours=12)  # 최대 12시간 관찰

    changes = []
    baseline = None
    for entry in prices:
        t = datetime.fromisoformat(entry["timestamp"])
        if t < start_time:
            continue
        if t > end_time:
            break

        if baseline is None:
            baseline = entry["price"]
            continue

        change = (entry["price"] - baseline) / baseline
        changes.append({"timestamp": entry["timestamp"], "change": change})

    if not changes:
        return 0, 0

    max_change = max(changes, key=lambda x: abs(x["change"]))
    duration = (datetime.fromisoformat(max_change["timestamp"]) - start_time).total_seconds() / 3600
    return max_change["change"], duration


def learn_from_events():
    events = load_json(EVENT_LOG_FILE)
    prices = load_json(PRICE_LOG_FILE)
    learning = defaultdict(lambda: {"count": 0, "avg_change": 0.0, "avg_duration": 0.0})

    for e in events:
        event_type = e.get("type")
        time = e.get("time")
        if not event_type or not time:
            continue

        change, duration = find_price_change(prices, time)

        if change == 0:
            continue

        stats = learning[event_type]
        stats["count"] += 1
        stats["avg_change"] = ((stats["avg_change"] * (stats["count"] - 1)) + change) / stats["count"]
        stats["avg_duration"] = ((stats["avg_duration"] * (stats["count"] - 1)) + duration) / stats["count"]

    save_json(EVENT_LEARNING_FILE, learning)
    print(f"[이벤트 학습 완료] {len(learning)}종류 이벤트 학습 저장됨.")


if __name__ == "__main__":
    learn_from_events()
