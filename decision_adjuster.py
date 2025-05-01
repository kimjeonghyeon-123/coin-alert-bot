from utils import moving_average, load_learning_stats, load_weights
from trend_angle_analyzer import analyze_trend_angle_and_inflection
import math

def adjust_confidence(entry_info, simulation_result):
    confidence = entry_info.get("confidence", 0.5)
    volume_factor = entry_info.get("volume_factor", 1.0)
    event_influence = entry_info.get("event_influence", 0.0)
    volatility_factor = entry_info.get("volatility_factor", 1.0)
    risk_weight = entry_info.get("risk_weight", 1.0)

    if volume_factor > 1.2:
        confidence += 0.03
    if volatility_factor < 0.8:
        confidence -= 0.03
    if event_influence > 0.5:
        confidence += 0.02
    confidence *= risk_weight
    confidence = max(0, min(1, confidence))

    smoothed_confidence = 1 / (1 + math.exp(-12 * (confidence - 0.5)))
    return smoothed_confidence

def extract_ma_value(ma):
    """dict 또는 숫자 중에서 value만 뽑아내는 함수."""
    if isinstance(ma, dict):
        return ma.get("value", 0)
    elif isinstance(ma, (int, float)):
        return ma
    else:
        return 0

def calculate_probability(prices, timestamps, pattern, trend, direction, events=None, current_time=None, volume_factor=1, risk_weight=1.0):
    weights = load_weights() or {}
    stats = load_learning_stats() or {}

    stats.setdefault("patterns", {})
    stats.setdefault("trend", {})
    stats.setdefault("direction", {})

    if isinstance(prices[0], dict):
        prices = [p.get("price", 0) for p in prices]

    change_rate_5m = (prices[-1] - prices[-2]) / prices[-2] * 100
    change_rate_30m = (prices[-1] - prices[-6]) / prices[-6] * 100
    change_rate_60m = (prices[-1] - prices[-12]) / prices[-12] * 100

    change_rate = change_rate_60m
    speed = abs(prices[-1] - prices[-12]) / (timestamps[-1] - timestamps[-12])

    ma5_raw = moving_average(prices, 5)
    ma20_raw = moving_average(prices, 20)
    ma60_raw = moving_average(prices, 60)

    ma5 = extract_ma_value(ma5_raw)
    ma20 = extract_ma_value(ma20_raw)
    ma60 = extract_ma_value(ma60_raw)

    trend_score = 0
    if all(isinstance(ma, (int, float)) for ma in [ma5, ma20, ma60]):
        if ma5 > ma20 and ma20 > ma60:
            trend_score += 1
            trend = "up"
        elif ma5 < ma20 and ma20 < ma60:
            trend_score -= 1
            trend = "down"

    pattern_score = 0.2 if pattern == "W-Pattern" else -0.2 if pattern == "M-Pattern" else 0

    base_probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    base_probability = max(0, min(1, base_probability))

    if direction == "long" and change_rate_5m > 2:
        base_probability += 0.05

    adjustment = 0
    if pattern and pattern in stats["patterns"]:
        p = stats["patterns"].get(pattern, {})
        total = p.get("success", 0) + p.get("fail", 0)
        if total > 5:
            winrate = p.get("success", 0) / total
            adjustment += (winrate - 0.5) * weights.get("pattern", 0)

    if trend and trend in stats["trend"]:
        t = stats["trend"].get(trend, {})
        total = t.get("success", 0) + t.get("fail", 0)
        if total > 5:
            winrate = t.get("success", 0) / total
            adjustment += (winrate - 0.5) * weights.get("trend", 0)

    if direction in stats["direction"]:
        d = stats["direction"].get(direction, {})
        total = d.get("success", 0) + d.get("fail", 0)
        if total > 5:
            winrate = d.get("success", 0) / total
            adjustment += (winrate - 0.5) * weights.get("direction", 0)

    adjusted_probability = base_probability + adjustment

    event_influence = 0.0
    if events and current_time:
        for e in events:
            event_time = e.get('timestamp', 0)
            duration = e.get('duration', 3600)
            elapsed = current_time - event_time
            if elapsed < duration:
                weight_factor = 1 - (elapsed / duration)
                impact = e.get('impact', 'low')
                if impact == "high":
                    event_influence += weights.get("event_high", 0) * weight_factor
                elif impact == "medium":
                    event_influence += weights.get("event_medium", 0) * weight_factor
                elif impact == "low":
                    event_influence += weights.get("event_low", 0) * weight_factor

    angle_info = analyze_trend_angle_and_inflection(prices)
    angle = angle_info.get("angle", 0)
    inflections = angle_info.get("inflection_points", [])

    angle_weight = weights.get("angle", 0)
    if abs(change_rate_5m) > 2:
        angle_weight *= 1.5

    if direction == "long" and angle > 50:
        adjusted_probability += angle_weight
    elif direction == "short" and angle < -50:
        adjusted_probability += angle_weight
    elif abs(angle) < 20:
        adjusted_probability -= angle_weight

    if inflections and abs(len(prices) - 1 - inflections[-1]) <= 2:
        adjusted_probability += weights.get("inflection", 0)

    if volume_factor > 1.2 and abs(change_rate_5m) > 2:
        adjusted_probability += 0.03

    entry_info = {
        "confidence": adjusted_probability,
        "volume_factor": volume_factor,
        "event_influence": event_influence,
        "volatility_factor": 1.0,
        "risk_weight": risk_weight
    }

    final_probability = adjust_confidence(entry_info, simulation_result={})
    return final_probability, ma5, ma20, ma60

