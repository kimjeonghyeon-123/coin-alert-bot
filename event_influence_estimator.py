# event_influence_estimator.py
import json
import os
import datetime
from price_fetcher import get_current_price

LEARNING_FILE = "event_learning.json"

# 이벤트 영향 추정

def estimate_event_impact(event_type, content_summary):
    if not os.path.exists(LEARNING_FILE):
        return {
            "impact_direction": "unknown",
            "win_rate": 0.5,
            "expected_duration": 3600  # 1시간 기본
        }

    with open(LEARNING_FILE, "r") as f:
        learning_data = json.load(f)

    type_data = learning_data.get(event_type)
    if not type_data:
        return {
            "impact_direction": "unknown",
            "win_rate": 0.5,
            "expected_duration": 3600
        }

    # 최근 데이터 우선 고려
    sorted_entries = sorted(type_data, key=lambda x: x["timestamp"], reverse=True)
    matching = [e for e in sorted_entries if content_summary.lower() in e["content_summary"].lower()]

    if matching:
        # 유사 이슈가 있으면 그걸 바탕으로 영향 추정
        top = matching[0]
        return {
            "impact_direction": top["price_movement_direction"],
            "win_rate": round(top["win_rate"], 2),
            "expected_duration": top["duration"]
        }
    else:
        # 유사 이슈가 없으면 해당 유형 평균
        total = len(type_data)
        if total == 0:
            return {
                "impact_direction": "unknown",
                "win_rate": 0.5,
                "expected_duration": 3600
            }

        up = sum(1 for d in type_data if d["price_movement_direction"] == "up")
        down = sum(1 for d in type_data if d["price_movement_direction"] == "down")
        avg_win_rate = sum(d["win_rate"] for d in type_data) / total
        avg_duration = sum(d["duration"] for d in type_data) / total

        direction = "up" if up > down else "down" if down > up else "unknown"

        return {
            "impact_direction": direction,
            "win_rate": round(avg_win_rate, 2),
            "expected_duration": int(avg_duration)
        }
