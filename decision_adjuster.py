import json
import os

LEARNING_STATS_PATH = "learning_stats.json"

def load_learning_stats():
    if not os.path.exists(LEARNING_STATS_PATH):
        return {
            "patterns": {},
            "trend": {},
            "direction": {},
            "events": {}
        }

    try:
        with open(LEARNING_STATS_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "patterns": {},
            "trend": {},
            "direction": {},
            "events": {}
        }

def adjust_confidence(base_confidence, detected_patterns=[], direction=None, trend=None, event_key=None):
    stats = load_learning_stats()
    confidence = base_confidence

    # 패턴 기반 보정
    for pattern in detected_patterns:
        pattern_stats = stats.get("patterns", {}).get(pattern)
        if pattern_stats:
            total = pattern_stats.get("success", 0) + pattern_stats.get("fail", 0)
            if total >= 5:
                success_rate = pattern_stats["success"] / total
                adjustment = (success_rate - 0.5) * 0.4  # ±20% 영향
                confidence += adjustment

    # 방향 기반 보정 (long/short)
    if direction:
        direction_stats = stats.get("direction", {}).get(direction)
        if direction_stats:
            total = direction_stats.get("success", 0) + direction_stats.get("fail", 0)
            if total >= 3:
                success_rate = direction_stats["success"] / total
                adjustment = (success_rate - 0.5) * 0.3  # ±15% 영향
                confidence += adjustment

    # 추세 기반 보정 (up/down/sideways 등)
    if trend:
        trend_stats = stats.get("trend", {}).get(trend)
        if trend_stats:
            total = trend_stats.get("success", 0) + trend_stats.get("fail", 0)
            if total >= 3:
                success_rate = trend_stats["success"] / total
                adjustment = (success_rate - 0.5) * 0.3  # ±15% 영향
                confidence += adjustment

    # 이벤트 기반 보정 (예: 'fomc_hawkish', 'cpi_hot' 등)
    if event_key:
        event_stats = stats.get("events", {}).get(event_key)
        if event_stats:
            total = event_stats.get("success", 0) + event_stats.get("fail", 0)
            if total >= 3:
                success_rate = event_stats["success"] / total
                adjustment = (success_rate - 0.5) * 0.2  # ±10% 영향
                confidence += adjustment

    # 안전 범위 내 보정
    confidence = max(0, min(1, confidence))
    return round(confidence, 4)
