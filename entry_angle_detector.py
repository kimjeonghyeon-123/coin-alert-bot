import time
from notifier import send_telegram_message
from price_logger import get_recent_prices
from price_fetcher import get_current_price
from cpi_tracker import get_latest_all_cpi_directions
from event_impact_estimator import estimate_cpi_impact_for_all
from chart_pattern_detector import detect_chart_patterns
from volume_analyzer import analyze_volume_behavior
from trend_detector import get_current_trend
from decision_adjuster import adjust_confidence
from direction_predictor import predict_both_directions
from utils import moving_average

MIN_WIN_RATE_THRESHOLD = 0.70

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

def check_realtime_entry_signal(is_pattern_allowed):
    history = get_recent_prices(60)
    if len(history) < 10:
        return

    prices = [x['price'] for x in history]
    timestamps = [x['timestamp'] for x in history]

    # 🔸 거래량 반영
    if 'volume' in history[0]:
        volumes = [x['volume'] for x in history]
        volume_factor = analyze_volume_behavior(volumes, prices)
        print(f"volume_factor: {volume_factor}")
    else:
        volumes = None
        volume_factor = 1
        print("⚠️ 거래량 데이터 없음")

    change_rate = (prices[-1] - prices[-6]) / prices[-6] * 100
    time_diff = timestamps[-1] - timestamps[-6]
    if time_diff == 0:
        return
    speed = abs(prices[-1] - prices[-6]) / time_diff

    ma5 = moving_average(prices, 5)
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)

    trend_score = 0
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            trend_score += 1
        elif ma5 < ma20 < ma60:
            trend_score -= 1

    # 🔹 양 방향 기초 확률 예측
    base_confidences = predict_both_directions(change_rate, volume_factor)

    # 🔍 차트 패턴 탐지
    patterns = []
    pattern = detect_chart_pattern(prices)
    if pattern:
        patterns.append(pattern)

    if patterns:
        for p in patterns:
            if not is_pattern_allowed():
                print(f"[진입 차단] 신뢰되지 않은 패턴: {p}")
                return

    trend = get_current_trend(prices, volumes)
    event_keys = get_latest_all_cpi_directions()

    # 🔹 양 방향 보정 확률 계산
    adjusted = {
        direction: adjust_confidence(
            confidence=conf["confidence"],
            detected_patterns=patterns,
            direction=direction,
            trend=trend,
            event_keys=event_keys,
            simulation_result={}  # 나중에 시뮬레이션 연동 가능
        )
        for direction, conf in base_confidences.items()
    }

    # 🔺 최적 방향 선택
    best_direction = max(adjusted, key=lambda d: adjusted[d])
    best_confidence = adjusted[best_direction]

    if best_confidence is None:
        print("[오류] 신뢰도 계산 실패: best_confidence가 None입니다.")
        return

    if best_confidence >= MIN_WIN_RATE_THRESHOLD:
        current_price = get_current_price()
        stop_loss = current_price * 0.985 if best_direction == "long" else current_price * 1.015
        take_profit = current_price * 1.02 if best_direction == "long" else current_price * 0.98
        stop_loss_pct = abs(current_price - stop_loss) / current_price * 100
        leverage = calculate_leverage(best_confidence, stop_loss_pct)

        # 📌 CPI 설명 메시지
        cpi_reason = ""
        if event_keys:
            cpi_infos = estimate_cpi_impact_for_all(event_keys)
            lines = []
            for key, info in cpi_infos.items():
                if info["known"]:
                    line = f"→ {key}: 평균 {info['average_change_percent']}%, 상승 확률 {info['positive_rate_percent']}% → *{info['bias']}*"
                    lines.append(line)
            if lines:
                cpi_reason = "\n\n*CPI 근거:*\n" + "\n".join(lines)

        signal_strength = "🔥 강력 신호" if best_confidence >= 0.90 else "✅ 추천 신호"

        message = f"""{signal_strength} *실시간 진입각 탐지!*  
*방향:* {best_direction.upper()}  
*현재가:* {current_price:.2f}  
*이동평균:* ma5={ma5:.2f}, ma20={ma20:.2f}, ma60={ma60:.2f}  
*패턴:* {', '.join(patterns) if patterns else '없음'}  
*예상 승률:* {best_confidence * 100:.1f}%  
*추천 레버리지:* {leverage}x  
*TP:* {take_profit:.2f}  
*SL:* {stop_loss:.2f}{cpi_reason}"""

        try:
            send_telegram_message(message)
        except Exception as e:
            print(f"[텔레그램 오류] 메시지 전송 실패: {e}")

        execute_entry(patterns, best_direction, current_price, stop_loss, take_profit)

def execute_entry(patterns, direction, entry_price, stop_loss, take_profit):
    print(f"[진입 실행] {', '.join(patterns) if patterns else '패턴 없음'} | {direction.upper()} | 진입가: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")

def detect_chart_pattern(prices):
    if len(prices) < 10:
        return None
    if prices[-1] > prices[-3] < prices[-5] and prices[-3] > prices[-5]:
        return "W-Pattern"
    elif prices[-1] < prices[-3] > prices[-5] and prices[-3] < prices[-5]:
        return "M-Pattern"
    return None







