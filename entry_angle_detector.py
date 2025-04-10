import json
import os
import time
import statistics
from notifier import send_telegram_message
from price_logger import get_recent_prices
from price_fetcher import get_current_price
from cpi_tracker import get_latest_cpi_direction
from event_impact_estimator import estimate_cpi_impact

# 이동평균 계산
def moving_average(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

# 간단한 차트 패턴 감지
def detect_chart_pattern(prices):
    if len(prices) < 5:
        return None
    p = [x['price'] for x in prices[-5:]]
    if p[0] > p[1] < p[2] > p[3] < p[4]:
        return "W-Pattern"
    if p[0] < p[1] > p[2] < p[3] > p[4]:
        return "M-Pattern"
    return None

# 추천 레버리지 계산
def calculate_leverage(win_rate, stop_loss_pct):
    base_leverage = 1 if stop_loss_pct > 3 else 2
    if win_rate >= 0.99:
        return base_leverage * 5
    elif win_rate >= 0.95:
        return base_leverage * 3
    elif win_rate >= 0.90:
        return base_leverage * 2
    else:
        return base_leverage

# 진입각 분석 및 실시간 감지
def check_realtime_entry_signal(is_pattern_allowed):
    history = get_recent_prices(60)
    if len(history) < 10:
        return

    prices = [x['price'] for x in history]
    timestamps = [x['timestamp'] for x in history]

    # 변화율 계산
    change_rate = (prices[-1] - prices[-6]) / prices[-6] * 100

    # 이동평균선
    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    # 추세 점수
    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
        elif ma5 < ma20 < ma60:
            trend_score -= 1

    # 속도 계산
    time_diff = timestamps[-1] - timestamps[-6]
    if time_diff == 0:
        return  # 속도 계산 불가
    speed = abs(prices[-1] - prices[-6]) / time_diff

    # 차트 패턴
    pattern = detect_chart_pattern(history)
    pattern_score = 0.2 if pattern == "W-Pattern" else -0.2 if pattern == "M-Pattern" else 0

    # 진입 확률 계산
    probability = 0.5 + (change_rate / 10) + (trend_score * 0.2) + pattern_score
    probability = max(0, min(1, probability))

    if probability >= 0.7:
        direction = "long" if change_rate > 0 else "short"

        # 신뢰되지 않은 패턴 차단
        if pattern and not is_pattern_allowed(pattern):
            print(f"[진입 차단] 신뢰되지 않은 패턴: {pattern}")
            return

        current_price = get_current_price()
        stop_loss = current_price * 0.98
        take_profit = current_price * 1.05
        stop_loss_pct = abs(current_price - stop_loss) / current_price * 100
        leverage = calculate_leverage(probability, stop_loss_pct)

        # 🧠 CPI 예측 근거 추가
        cpi_dir = get_latest_cpi_direction()
        cpi_reason = ""
        if cpi_dir:
            cpi_info = estimate_cpi_impact(cpi_dir)
            if cpi_info["known"]:
                cpi_reason = f"\n*CPI 근거:* '{cpi_dir}' 방향은 과거 평균 {cpi_info['average_change_percent']}%, 상승 확률 {cpi_info['positive_rate_percent']}%로 '{cpi_info['bias']}' 경향"

        message = f"""🚨 *실시간 진입각 탐지!*

*방향:* {direction.upper()}
*현재가:* {current_price:.2f}
*이동평균:* ma5={ma5:.2f}, ma20={ma20:.2f}, ma60={ma60:.2f}
*패턴:* {pattern or '없음'}
*예상 승률:* {probability * 100:.1f}%
*추천 레버리지:* {leverage}x
*TP:* {take_profit:.2f}
*SL:* {stop_loss:.2f}{cpi_reason}
"""
        try:
            send_telegram_message(message)
        except Exception as e:
            print(f"[텔레그램 오류] 메시지 전송 실패: {e}")

        execute_entry(pattern, direction, current_price, stop_loss, take_profit)

# 진입 실행 함수 (후속 자동화 가능)
def execute_entry(pattern, direction, entry_price, stop_loss, take_profit):
    print(f"[진입 실행] {pattern or '패턴 없음'} | {direction} | 진입가: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")
