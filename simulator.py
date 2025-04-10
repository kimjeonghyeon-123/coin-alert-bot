import time
import json
import os
from price_logger import get_recent_prices
from notifier import send_telegram_message
from entry_angle_detector import detect_chart_pattern
from decision_adjuster import calculate_probability


def save_prediction(prediction):
    try:
        with open("prediction_log.json", "r") as f:
            history = json.load(f)
    except:
        history = []

    history.append(prediction)
    with open("prediction_log.json", "w") as f:
        json.dump(history[-1000:], f, indent=2)


def evaluate_predictions():
    try:
        with open("prediction_log.json", "r") as f:
            predictions = json.load(f)
    except:
        return

    now = int(time.time())
    updated_predictions = []
    for p in predictions:
        if 'result' in p:
            updated_predictions.append(p)
            continue

        if now - p['timestamp'] >= 60 * 60 * 3:
            future_prices = get_recent_prices(1)  # 가장 최근 가격 가져옴
            if not future_prices:
                continue
            future_price = future_prices[-1]['price']
            entry = p['entry']
            direction = p['direction']
            result = "success" if (
                (direction == "long" and future_price >= p['take_profit']) or
                (direction == "short" and future_price <= p['take_profit'])
            ) else "fail"
            p['result'] = result
            update_learning_stats(p)
        updated_predictions.append(p)

    with open("prediction_log.json", "w") as f:
        json.dump(updated_predictions[-1000:], f, indent=2)


def update_learning_stats(prediction):
    try:
        with open("learning_stats.json", "r") as f:
            stats = json.load(f)
    except:
        stats = {}

    key = prediction['pattern'] or 'none'
    if key not in stats:
        stats[key] = {"success": 0, "fail": 0}

    stats[key][prediction['result']] += 1

    with open("learning_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    update_weights_from_learning(stats)


def update_weights_from_learning(stats):
    weights = {}
    for key, s in stats.items():
        total = s['success'] + s['fail']
        if total < 3:
            weights[key] = 1.0  # 초기 가중치
        else:
            success_rate = s['success'] / total
            weights[key] = round(0.5 + success_rate, 2)

    with open("weights.json", "w") as f:
        json.dump(weights, f, indent=2)


def run_simulation(recent_events=None):
    evaluate_predictions()

    history = get_recent_prices(120)
    if len(history) < 20:
        return

    prices = [x['price'] for x in history]
    timestamps = [x['timestamp'] for x in history]
    pattern = detect_chart_pattern(history)
    direction = "long" if len(prices) >= 12 and prices[-1] > prices[-12] else "short"
    trend = None
    current_time = int(time.time())

    win_rate, ma5, ma20, ma60 = calculate_probability(
        prices, timestamps, pattern, trend, direction,
        events=recent_events, current_time=current_time
    )

    entry = prices[-1]
    stop_loss = entry * (0.98 if direction == "long" else 1.02)
    take_profit = entry * (1.02 if direction == "long" else 0.98)

    message = f"""📊 *시뮬레이션 결과*

*방향:* {direction.capitalize()}
*진입가:* {entry:.2f}
*손절가:* {stop_loss:.2f}
*익절가:* {take_profit:.2f}
*이동평균:* ma5={ma5:.2f if ma5 else 'N/A'}, ma20={ma20:.2f if ma20 else 'N/A'}, ma60={ma60:.2f if ma60 else 'N/A'}
*패턴:* {pattern or '없음'}
*예상 승률:* {win_rate * 100:.1f}%
"""
    send_telegram_message(message)

    # 저장
    prediction = {
        "timestamp": current_time,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "pattern": pattern,
        "trend": trend,
        "win_rate": win_rate
    }
    save_prediction(prediction)


def simulate_entry(price_slice, current_price, simulate_mode=False, recent_events=None):
    if len(price_slice) < 20:
        return None

    prices = [float(x['close']) for x in price_slice]
    timestamps = [int(x['timestamp']) for x in price_slice]
    pattern = detect_chart_pattern(price_slice)
    direction = "long" if len(prices) >= 12 and prices[-1] > prices[-12] else "short"
    trend = None
    current_time = int(time.time())

    win_rate, ma5, ma20, ma60 = calculate_probability(
        prices, timestamps, pattern, trend, direction,
        events=recent_events, current_time=current_time
    )

    stop_loss = current_price * (0.98 if direction == "long" else 1.02)
    take_profit = current_price * (1.02 if direction == "long" else 0.98)

    result = {
        "timestamp": current_time,
        "direction": direction,
        "entry": current_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "win_rate": win_rate,
        "pattern": pattern,
        "trend": trend,
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60
    }

    if simulate_mode:
        print("🔍 시뮬레이션 (simulate_mode=True):", result)

    try:
        with open("simulation_results.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(result)
    with open("simulation_results.json", "w") as f:
        json.dump(data[-500:], f, indent=2)

    return result

