# event_impact_applier.py
import json
import os
from datetime import datetime

EVENT_IMPACT_FILE = "event_impact_learning.json"


def load_event_impact_data():
    if not os.path.exists(EVENT_IMPACT_FILE):
        return {}
    with open(EVENT_IMPACT_FILE, 'r') as f:
        return json.load(f)


def evaluate_event_impact(event_type, direction_hint):
    """
    event_type: str - 예: 'FOMC', 'Elon Musk', 'CPI'
    direction_hint: str - 'long' 또는 'short', 예상 방향이 있다면
    """
    data = load_event_impact_data()
    impact_info = data.get(event_type)

    if not impact_info:
        return None  # 학습된 이벤트가 아님

    win_rate = impact_info.get("win_rate")
    avg_duration = impact_info.get("avg_duration")
    confidence = impact_info.get("confidence")
    direction = impact_info.get("direction")

    # 예상 방향과 일치 여부에 따라 보정
    direction_match = direction == direction_hint
    final_win_rate = win_rate * 1.1 if direction_match else win_rate * 0.9

    return {
        "win_rate": round(min(final_win_rate, 1.0), 3),
        "direction": direction,
        "avg_duration": avg_duration,
        "confidence": confidence
    }


# 예시 실행 (테스트용)
if __name__ == "__main__":
    example = evaluate_event_impact("Elon Musk", "long")
    print("[EVENT IMPACT 평가]", example)
