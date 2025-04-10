# simulator.py

import time
import json
from price_logger import get_recent_prices
from notifier import send_telegram_message
from entry_angle_detector import moving_average, detect_chart_pattern

def load_learning_stats():
    try:
        with open("learning_stats.json", "r") as f:
            return json.load(f)
    except:
        return {}

def calculate_probability(prices, timestamps, pattern, trend, direction):
    change_rate = (prices[-1] - prices[-12]) / prices[-12] * 100
    speed = abs(prices[-1] - prices[-12]) / (timestamps[-1] - timestamps[-12])

    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
            trend = "up"
        elif ma5 < ma20 < ma60:
            trend_score -= 1
            trend = "down"

    pattern_score = 0.2 if pattern == "W-Pattern" else -0.2 if pattern == "M-Pattern" else 0
    base_probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    base_probability = max(0, min(1, base_probability))

    # 📘 학습 통계 기반 보정
    stats = load_learning_stats()
    adjustment = 0

    if pattern and pattern in stats.get("patterns", {}):
        p = stats["patterns"][pattern]
        total = p["success"] + p["fail"]
        if total > 5:
            winrate = p["success"] / total
            adjustment += (winrate - 0.5) * 0.4

    if trend and trend in stats.get("trend", {}):
        t = stats["trend"][trend]
        total = t["success"] + t["fail"]
        if total > 5:
            winrate = t["success"] / total
            adjustment += (winrate - 0.5) * 0.3

    if direction in stats.get("direction", {}):
        d = stats["direction"][direction]
        total = d["success"] + d["fail"]
        if total > 5:
            winrate = d["success"] / total
            adjustment += (winrate - 0.5) * 0.3

    final_probability = max(0, min(1, base_probability + adjustment))

    return final_probability, ma5, ma20, ma60

# ✅ 실시간 시뮬레이션
def run_simulation(recent_events=None):
    history = get_recent_prices(120)
    if len(history) < 20:
        return

    prices = [x['price'] for x in history]
    timestamps = [x['timestamp'] for x in history]
    pattern = detect_chart_pattern(history)
    direction = "long" if prices[-1] > prices[-12] else "short"
    trend = None

    win_rate, ma5, ma20, ma60 = calculate_probability(prices, timestamps, pattern, trend, direction)

    # ✅ 이벤트 영향 추가
    if recent_events:
        for e in recent_events:
            if e['impact'] == "high":
                win_rate += 0.2
            elif e['impact'] == "medium":
                win_rate += 0.1
        win_rate = max(0, min(1, win_rate))

    entry = prices[-1]
    stop_loss = entry * (0.98 if direction == "long" else 1.02)
    take_profit = entry * (1.02 if direction == "long" else 0.98)

    message = f"""📊 *시뮬레이션 결과*

*방향:* {direction.capitalize()}
*진입가:* {entry:.2f}
*손절가:* {stop_loss:.2f}
*익절가:* {take_profit:.2f}
*이동평균:* ma5={ma5:.2f}, ma20={ma20:.2f}, ma60={ma60:.2f}
*패턴:* {pattern or '없음'}
*예상 승률:* {win_rate * 100:.1f}%
"""
    send_telegram_message(message)

# ✅ 외부에서도 사용할 수 있는 시뮬레이션 함수
def simulate_entry(price_slice, current_price, simulate_mode=False):
    prices = [float(x['close']) for x in price_slice]
    timestamps = [int(x['timestamp']) for x in price_slice]
    pattern = detect_chart_pattern(price_slice)
    direction = "long" if prices[-1] > prices[-12] else "short"
    trend = None

    win_rate, ma5, ma20, ma60 = calculate_probability(prices, timestamps, pattern, trend, direction)

    stop_loss = current_price * (0.98 if direction == "long" else 1.02)
    take_profit = current_price * (1.02 if direction == "long" else 0.98)

    if simulate_mode:
        print(f"[SIM] Direction: {direction}, WinRate: {win_rate:.2f}, Pattern: {pattern or '없음'}")

    return {
        "direction": direction,
        "entry_price": current_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "win_rate": win_rate,
        "pattern": pattern,
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60,
    }
