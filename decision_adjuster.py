import json
import time
from entry_angle_detector import moving_average
from trend_angle_analyzer import analyze_trend_angle, detect_inflection_points

# 외부 가중치 로딩
def load_weights():
    try:
        with open("weights.json", "r") as f:
            return json.load(f)
    except:
        # 기본값
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

def calculate_probability(prices, timestamps, pattern, trend, direction, events=None, current_time=None):
    """
    실시간 또는 시뮬레이션 시 진입 방향 확률을 계산하는 핵심 함수.
    다양한 요소(이동평균, 속도, 패턴, 이벤트, 학습 결과 등)를 조합하여 확률을 계산한다.
    """
    weights = load_weights()

    # --- 1. 변화율 및 속도 ---
    change_rate = (prices[-1] - prices[-12]) / prices[-12] * 100
    speed = abs(prices[-1] - prices[-12]) / (timestamps[-1] - timestamps[-12])

    # --- 2. 이동 평균 계산 ---
    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    # --- 3. 추세 판단 ---
    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
            trend = "up"
        elif ma5 < ma20 < ma60:
            trend_score -= 1
            trend = "down"

    # --- 4. 패턴 점수 ---
    pattern_score = 0.2 if pattern == "W-Pattern" else -0.2 if pattern == "M-Pattern" else 0

    # --- 5. 기초 승률 계산 ---
    base_probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    base_probability = max(0, min(1, base_probability))

    # --- 6. 학습 기반 조정 ---
    stats = load_learning_stats()
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

    # --- 7. 빗각 기반 조정 ---
    angle = analyze_trend_angle(prices)
    if direction == "long" and angle > 50:
        final_probability += weights["angle"]
    elif direction == "short" and angle < -50:
        final_probability += weights["angle"]
    elif abs(angle) < 20:
        final_probability -= weights["angle"]

    # --- 8. 변곡점 보정 ---
    inflections = detect_inflection_points(prices)
    if inflections and abs(len(prices) - 1 - inflections[-1]) <= 2:
        final_probability += weights["inflection"]

    # --- 9. 이벤트 보정 ---
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
