import json
import time
from utils import moving_average
from trend_angle_analyzer import analyze_trend_angle_and_inflection

# 외부 가중치 로딩
def load_weights():
    try:
        with open("weights.json", "r") as f:
            return json.load(f)
    except:
        return {
            "pattern": 0.4,
            "trend": 0.3,
            "direction": 0.3,
            "angle": 0.05,
            "inflection": 0.03,
            "event_high": 0.2,
            "event_medium": 0.1,
            "event_low": 0.05
        }

# 학습 데이터 로딩
def load_learning_stats():
    try:
        with open("learning_stats.json", "r") as f:
            return json.load(f)
    except:
        return {}

def calculate_probability(prices, timestamps, pattern, trend, direction, events=None, current_time=None, volume_factor=1):
    weights = load_weights()
    stats = load_learning_stats()

    # 가격 변화율, 속도 계산
    change_rate = (prices[-1] - prices[-12]) / prices[-12] * 100
    speed = abs(prices[-1] - prices[-12]) / (timestamps[-1] - timestamps[-12])

    # 이동 평균
    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    # 추세 분석
    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
            trend = "up"
        elif ma5 < ma20 < ma60:
            trend_score -= 1
            trend = "down"

    # 패턴 점수
    pattern_score = 0.2 if pattern == "W-Pattern" else -0.2 if pattern == "M-Pattern" else 0

    # 초기 확률
    base_probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    base_probability = max(0, min(1, base_probability))

    # 학습 기반 가중치 조정
    adjustment = 0

    if pattern and pattern in stats.get("patterns", {}):
        p = stats["patterns"][pattern]
        total = p["success"] + p["fail"]
        if total > 5:
            winrate = p["success"] / total
            adjustment += (winrate - 0.5) * weights["pattern"]

    if trend and trend in stats.get("trend", {}):
        t = stats["trend"][trend]
        total = t["success"] + t["fail"]
        if total > 5:
            winrate = t["success"] / total
            adjustment += (winrate - 0.5) * weights["trend"]

    if direction in stats.get("direction", {}):
        d = stats["direction"][direction]
        total = d["success"] + d["fail"]
        if total > 5:
            winrate = d["success"] / total
            adjustment += (winrate - 0.5) * weights["direction"]

    final_probability = max(0, min(1, base_probability + adjustment))

    # 거래량 반영
    final_probability *= volume_factor
    final_probability = max(0, min(1, final_probability))

    # 추세 각도 반영
    angle_info = analyze_trend_angle_and_inflection(prices)
    angle = angle_info["angle"]
    inflections = angle_info["inflection_points"]

    if direction == "long" and angle > 50:
        final_probability += weights["angle"]
    elif direction == "short" and angle < -50:
        final_probability += weights["angle"]
    elif abs(angle) < 20:
        final_probability -= weights["angle"]

    # 꺾이는 지점 반영
    if inflections and abs(len(prices) - 1 - inflections[-1]) <= 2:
        final_probability += weights["inflection"]

    # 이벤트 영향 반영
    if events and current_time:
        for e in events:
            event_time = e['timestamp']
            duration = e.get('duration', 3600)
            elapsed = current_time - event_time
            if elapsed < duration:
                weight_factor = 1 - (elapsed / duration)
                impact = e.get('impact', 'low')
                if impact == "high":
                    final_probability += weights["event_high"] * weight_factor
                elif impact == "medium":
                    final_probability += weights["event_medium"] * weight_factor
                elif impact == "low":
                    final_probability += weights["event_low"] * weight_factor

    return max(0, min(1, final_probability)), ma5, ma20, ma60


def adjust_confidence(
    base_confidence, detected_patterns, direction, trend, event_key
):
    if trend == "up" and direction == "long":
        base_confidence += 0.05
    elif trend == "down" and direction == "short":
        base_confidence += 0.05
    else:
        base_confidence -= 0.03

    if detected_patterns:
        for pattern in detected_patterns:
            if pattern == "W-Pattern" and direction == "long":
                base_confidence += 0.07
            elif pattern == "M-Pattern" and direction == "short":
                base_confidence += 0.07
            else:
                base_confidence -= 0.02

    if event_key == "hot" and direction == "long":
        base_confidence += 0.03
    elif event_key == "cool" and direction == "short":
        base_confidence += 0.03
    elif event_key == "inline":
        base_confidence += 0.01
    else:
        base_confidence -= 0.02

    return max(0, min(1, base_confidence))




