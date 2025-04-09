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

    message = f"📊 *시뮬레이션 결과*

*방향:* {direction}
*진입가:* {entry:.2f}
*손절가:* {stop_loss:.2f}
*익절가:* {take_profit:.2f}
*이동평균:* ma5={ma5:.2f}, ma20={ma20:.2f}, ma60={ma60:.2f}
*패턴:* {pattern or '없음'}
*예상 승률:* {probability * 100:.1f}%"
    send_telegram_message(message)

    # 결과 저장 후 향후 개선점 학습에도 활용 가능 (보류)
