import json
import os
import time

LEARNING_FILE = "learning_stats.json"

def load_stats():
    if os.path.exists(LEARNING_FILE):
        with open(LEARNING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(LEARNING_FILE, "w") as f:
        json.dump(stats, f, indent=2)

# 📌 예측 결과 기록
def update_prediction_result(category, key, success: bool):
    stats = load_stats()
    if category not in stats:
        stats[category] = {}

    if key not in stats[category]:
        stats[category][key] = {"success": 0, "fail": 0}

    if success:
        stats[category][key]["success"] += 1
    else:
        stats[category][key]["fail"] += 1

    save_stats(stats)

# 📌 이벤트 지속 시간 학습
def update_event_duration(event_type, actual_duration):
    stats = load_stats()
    if "event_duration" not in stats:
        stats["event_duration"] = {}

    if event_type not in stats["event_duration"]:
        stats["event_duration"][event_type] = {"total_duration": 0, "count": 0}

    stats["event_duration"][event_type]["total_duration"] += actual_duration
    stats["event_duration"][event_type]["count"] += 1

    save_stats(stats)

# 📌 평균 이벤트 지속 시간 조회
def get_average_event_duration(event_type):
    stats = load_stats()
    info = stats.get("event_duration", {}).get(event_type)
    if info and info["count"] > 0:
        return info["total_duration"] / info["count"]
    return 3600  # 기본값 1시간
