from utils import moving_average, load_learning_stats, load_weights
from trend_angle_analyzer import analyze_trend_angle_and_inflection  # 수정된 모듈 이름

def calculate_probability(prices, timestamps, pattern, trend, direction, events=None, current_time=None, volume_factor=1):
    weights = load_weights()
    stats = load_learning_stats()

    # ░░ 가격 변화율 계산 ░░
    change_rate_5m = (prices[-1] - prices[-2]) / prices[-2] * 100
    change_rate_30m = (prices[-1] - prices[-6]) / prices[-6] * 100
    change_rate_60m = (prices[-1] - prices[-12]) / prices[-12] * 100

    # 기존 change_rate와 speed 유지
    change_rate = change_rate_60m
    speed = abs(prices[-1] - prices[-12]) / (timestamps[-1] - timestamps[-12])

    # 이동 평균
    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    # ░░ 추세 분석 ░░
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

    # ░░ 초기 승률 ░░
    base_probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    base_probability = max(0, min(1, base_probability))

    # ░░ 변화율이 2% 이상이면 long 방향 보정 ░░
    if direction == "long" and change_rate_5m > 2:
        base_probability += 0.05

    # ░░ 학습 기반 가중치 보정 ░░
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

    # ░░ 거래량 반영 ░░
    final_probability *= volume_factor
    final_probability = max(0, min(1, final_probability))

    # ░░ 추세 각도 및 inflection 분석 ░░
    angle_info = analyze_trend_angle_and_inflection(prices)
    angle = angle_info["angle"]
    inflections = angle_info["inflection_points"]

    # ░░ 변화율이 클수록 inflection 가능성 → angle 보정 가중치 증폭 ░░
    angle_weight = weights["angle"]
    if abs(change_rate_5m) > 2:
        angle_weight *= 1.5

    if direction == "long" and angle > 50:
        final_probability += angle_weight
    elif direction == "short" and angle < -50:
        final_probability += angle_weight
    elif abs(angle) < 20:
        final_probability -= angle_weight

    # ░░ inflection 지점 인접 여부 보정 ░░
    if inflections and abs(len(prices) - 1 - inflections[-1]) <= 2:
        final_probability += weights["inflection"]

    # ░░ 거래량 + 변화율 급등 시 추가 가중치 ░░
    if volume_factor > 1.2 and abs(change_rate_5m) > 2:
        final_probability += 0.03

    # ░░ 이벤트 영향 반영 ░░
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







