import time
from notifier import send_telegram_message
from price_logger import get_recent_prices
from price_fetcher import get_current_price
from cpi_tracker import get_latest_cpi_direction
from event_impact_estimator import estimate_cpi_impact
from chart_pattern_detector import detect_chart_patterns
from volume_analyzer import analyze_volume_behavior
from trend_detector import get_current_trend
from decision_adjuster import adjust_confidence
from direction_predictor import predict_direction
from utils import moving_average  

MIN_WIN_RATE_THRESHOLD = 0.70

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

    # 변화율 및 속도
    change_rate = (prices[-1] - prices[-6]) / prices[-6] * 100
    time_diff = timestamps[-1] - timestamps[-6]
    if time_diff == 0:
        return
    speed = abs(prices[-1] - prices[-6]) / time_diff

    # 이동평균
    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)
    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
        elif ma5 < ma20 < ma60:
            trend_score -= 1

    # 방향 예측
    direction, base_confidence = predict_direction(change_rate)

    # 패턴 감지
    patterns = detect_chart_patterns()
    if patterns:
        for p in patterns:
            if not is_pattern_allowed(p):
                print(f"[진입 차단] 신뢰되지 않은 패턴: {p}")
                return

    # 거래량 영향 분석
    volume_factor = analyze_volume_behavior()

    # 이벤트 및 트렌드
    trend = get_current_trend()
    event_key = get_latest_cpi_direction()

    # 보정된 확률 계산
    adjusted_confidence = adjust_confidence(
        base_confidence=base_confidence * volume_factor,
        detected_patterns=patterns,
        direction=direction,
        trend=trend,
        event_key=event_key
    )

    # 기준 넘으면 알림
    if adjusted_confidence >= MIN_WIN_RATE_THRESHOLD:
        current_price = get_current_price()
        stop_loss = current_price * 0.985 if direction == "long" else current_price * 1.015
        take_profit = current_price * 1.02 if direction == "long" else current_price * 0.98
        stop_loss_pct = abs(current_price - stop_loss) / current_price * 100
        leverage = calculate_leverage(adjusted_confidence, stop_loss_pct)

        # CPI 상세 설명
        cpi_reason = ""
        if event_key:
            cpi_info = estimate_cpi_impact(event_key)
            if cpi_info["known"]:
                cpi_reason = f"\n*CPI 근거:* '{event_key}'은 과거 평균 {cpi_info['average_change_percent']}%, 상승 확률 {cpi_info['positive_rate_percent']}% → '{cpi_info['bias']}' 경향"

        # 강력 신호 구분
        signal_strength = "🔥 강력 신호" if adjusted_confidence >= 0.90 else "✅ 추천 신호"

        message = f"""{signal_strength} *실시간 진입각 탐지!*  
*방향:* {direction.upper()}  
*현재가:* {current_price:.2f}  
*이동평균:* ma5={ma5:.2f}, ma20={ma20:.2f}, ma60={ma60:.2f}  
*패턴:* {', '.join(patterns) if patterns else '없음'}  
*예상 승률:* {adjusted_confidence * 100:.1f}%  
*추천 레버리지:* {leverage}x  
*TP:* {take_profit:.2f}  
*SL:* {stop_loss:.2f}{cpi_reason}"""

        try:
            send_telegram_message(message)
        except Exception as e:
            print(f"[텔레그램 오류] 메시지 전송 실패: {e}")

        execute_entry(patterns, direction, current_price, stop_loss, take_profit)

# 진입 실행 함수
def execute_entry(patterns, direction, entry_price, stop_loss, take_profit):
    print(f"[진입 실행] {', '.join(patterns) if patterns else '패턴 없음'} | {direction.upper()} | 진입가: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")

def detect_chart_pattern(prices):
    # 예시 로직: 가격이 저점을 두 번 찍으면 W-Pattern
    if len(prices) < 10:
        return None
    if prices[-1] > prices[-3] < prices[-5] and prices[-3] > prices[-5]:
        return "W-Pattern"
    elif prices[-1] < prices[-3] > prices[-5] and prices[-3] < prices[-5]:
        return "M-Pattern"
    return None


  

