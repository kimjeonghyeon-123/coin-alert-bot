# simulator.py
import time
from price_logger import get_recent_prices
from notifier import send_telegram_message
from entry_angle_detector import moving_average, detect_chart_pattern

# 간단 시뮬레이션
def run_simulation():
    history = get_recent_prices(120)
    if len(history) < 20:
        return

    prices = [x['price'] for x in history]
    timestamps = [x['timestamp'] for x in history]

    change_rate = (prices[-1] - prices[-12]) / prices[-12] * 100
    speed = abs(prices[-1] - prices[-12]) / (timestamps[-1] - timestamps[-12])

    # 이평선
    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    # 추세 방향
    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
        elif ma5 < ma20 < ma60:
            trend_score -= 1

    # 패턴 분석
    pattern = detect_chart_pattern(history)
    pattern_score = 0.2 if pattern == "W-Pattern" else -0.2 if pattern == "M-Pattern" else 0

    # 종합 확률
    probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    probability = max(0, min(1, probability))

    direction = "Long" if change_rate > 0 else "Short"
    entry = prices[-1]
    stop_loss = entry * (0.98 if direction == "Long" else 1.02)
    take_profit = entry * (1.02 if direction == "Long" else 0.98)

    message = f"""📊 *시뮬레이션 결과*

*방향:* {direction}
*진입가:* {entry:.2f}
*손절가:* {stop_loss:.2f}
*익절가:* {take_profit:.2f}
*이동평균:* ma5={ma5:.2f}, ma20={ma20:.2f}, ma60={ma60:.2f}
*패턴:* {pattern or '없음'}
*예상 승률:* {probability * 100:.1f}%
"""
    send_telegram_message(message)
    # 결과 저장 후 향후 개선점 학습에도 활용 가능 (보류)


# 외부에서도 사용할 수 있는 시뮬레이션 함수
import json
from entry_angle_detector import moving_average, detect_chart_pattern

def load_learning_stats():
    try:
        with open("learning_stats.json", "r") as f:
            return json.load(f)
    except:
        return {}

def simulate_entry(price_slice, current_price, simulate_mode=False):
    prices = [float(x['close']) for x in price_slice]
    timestamps = [int(x['timestamp']) for x in price_slice]

    change_rate = (prices[-1] - prices[-12]) / prices[-12] * 100
    speed = abs(prices[-1] - prices[-12]) / (timestamps[-1] - timestamps[-12])

    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    trend_score = 0
    trend = None
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
            trend = "up"
        elif ma5 < ma20 < ma60:
            trend_score -= 1
            trend = "down"

    pattern = detect_chart_pattern(price_slice)
    pattern_score = 0.2 if pattern == "W-Pattern" else -0.2 if pattern == "M-Pattern" else 0

    base_probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    base_probability = max(0, min(1, base_probability))

    direction = "long" if change_rate > 0 else "short"

    # 📘 학습 통계 적용
    stats = load_learning_stats()
    adjustment = 0

    # 패턴 보정
    if pattern and pattern in stats.get("patterns", {}):
        p = stats["patterns"][pattern]
        total = p["success"] + p["fail"]
        if total > 5:
            winrate = p["success"] / total
            adjustment += (winrate - 0.5) * 0.4  # 최대 ±0.2 보정

    # 추세 보정
    if trend and trend in stats.get("trend", {}):
        t = stats["trend"][trend]
        total = t["success"] + t["fail"]
        if total > 5:
            winrate = t["success"] / total
            adjustment += (winrate - 0.5) * 0.3

    # 방향 보정
    if direction in stats.get("direction", {}):
        d = stats["direction"][direction]
        total = d["success"] + d["fail"]
        if total > 5:
            winrate = d["success"] / total
            adjustment += (winrate - 0.5) * 0.3

    final_probability = max(0, min(1, base_probability + adjustment))

    stop_loss = current_price * (0.98 if direction == "long" else 1.02)
    take_profit = current_price * (1.02 if direction == "long" else 0.98)

    return {
        "direction": direction,
        "entry_price": current_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "win_rate": final_probability,
        "pattern": pattern,
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60,
    }
