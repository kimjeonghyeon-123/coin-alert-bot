# entry_angle_detector.py
import json
import os
import time
import statistics
from notifier import send_telegram_message
from price_logger import get_recent_prices


# 이동평균 계산
def moving_average(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period


# 차트 패턴 감지 (간단한 예시)
def detect_chart_pattern(prices):
    if len(prices) < 5:
        return None
    p = [x['price'] for x in prices[-5:]]
    if p[0] > p[1] < p[2] > p[3] < p[4]:
        return "W-Pattern"
    if p[0] < p[1] > p[2] < p[3] > p[4]:
        return "M-Pattern"
    return None


# 진입각 계산 (확률 + 볼륨 + 이평선 + 패턴)
def analyze_entry():
    history = get_recent_prices(60)
    if len(history) < 10:
        return

    prices = [x['price'] for x in history]
    timestamps = [x['timestamp'] for x in history]

    # 가격 변화율
    change_rate = (prices[-1] - prices[-6]) / prices[-6] * 100

    # 이동평균선
    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    # 이동평균 기반 추세
    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1  # 상승
        elif ma5 < ma20 < ma60:
            trend_score -= 1  # 하락

    # 최근 가격 변화 속도
    speed = abs(prices[-1] - prices[-6]) / (timestamps[-1] - timestamps[-6])

    # 차트 패턴
    pattern = detect_chart_pattern(history)
    pattern_score = 0.2 if pattern in ["W-Pattern"] else -0.2 if pattern == "M-Pattern" else 0

    # 최종 확률 계산
    probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    probability = max(0, min(1, probability))

    if probability >= 0.7:
        direction = "Long" if change_rate > 0 else "Short"
        message = f"🚨 *실시간 진입각 탐지!*

*방향:* {direction}
*현재가:* {prices[-1]:.2f}
*이동평균:* ma5={ma5:.2f}, ma20={ma20:.2f}, ma60={ma60:.2f}
*패턴:* {pattern or '없음'}
*예상 승률:* {probability * 100:.1f}%"
        send_telegram_message(message)
