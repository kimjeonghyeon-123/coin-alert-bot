import time
import json
import os
import traceback
from typing import List, Optional, Dict, Any
from price_logger import get_recent_prices
from notifier import send_telegram_message
from entry_angle_detector import detect_chart_pattern
from decision_adjuster import calculate_probability

PREDICTION_LOG_FILE = "prediction_log.json"
LEARNING_STATS_FILE = "learning_stats.json"
WEIGHTS_FILE = "weights.json"
SIMULATION_RESULTS_FILE = "simulation_results.json"


def load_json(file_path: str, default: Any) -> Any:
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def save_json(file_path: str, data: Any, limit: Optional[int] = None):
    if limit is not None and isinstance(data, list):
        data = data[-limit:]
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def save_prediction(prediction: Dict[str, Any]):
    history = load_json(PREDICTION_LOG_FILE, [])
    history.append(prediction)
    save_json(PREDICTION_LOG_FILE, history, limit=1000)
    if prediction.get("result"):
        update_learning_stats(prediction)


def evaluate_predictions():
    predictions = load_json(PREDICTION_LOG_FILE, [])
    now = int(time.time())
    updated_predictions = []

    for p in predictions:
        if 'result' in p:
            updated_predictions.append(p)
            continue

        if now - p.get('timestamp', 0) >= 60 * 60 * 3:
            future_prices = get_recent_prices(1)
            if not future_prices:
                updated_predictions.append(p)
                continue

            future_price = future_prices[-1].get('price')
            direction = p.get('direction')
            take_profit = p.get('take_profit')

            if future_price is None or direction not in ["long", "short"] or take_profit is None:
                updated_predictions.append(p)
                continue

            is_success = (
                (direction == "long" and future_price >= take_profit) or
                (direction == "short" and future_price <= take_profit)
            )
            result = "success" if is_success else "fail"
            p['result'] = result
            update_learning_stats(p)

            try:
                result_msg = f"""✅ *[3시간 전 예측 결과]*

*방향:* {direction}
*예측가:* {p['entry']:.2f}
*익절가:* {take_profit:.2f}
*실제가격:* {future_price:.2f}
*결과:* {"🎯 성공!" if result == "success" else "❌ 실패"}
"""
                time.sleep(60)
                send_telegram_message(result_msg)
            except Exception:
                traceback.print_exc()

        updated_predictions.append(p)

    save_json(PREDICTION_LOG_FILE, updated_predictions, limit=1000)


def update_learning_stats(prediction: Dict[str, Any]):
    if "result" not in prediction:
        return

    stats = load_json(LEARNING_STATS_FILE, {})
    key = prediction.get('pattern') or 'none'

    if key not in stats:
        stats[key] = {"success": 0, "fail": 0}

    if prediction['result'] in stats[key]:
        stats[key][prediction['result']] += 1

    save_json(LEARNING_STATS_FILE, stats)
    update_weights_from_learning(stats)


def update_weights_from_learning(stats: Dict[str, Dict[str, int]]):
    weights = {}
    for key, record in stats.items():
        total = record['success'] + record['fail']
        if total < 3:
            weights[key] = 1.0
        else:
            success_rate = record['success'] / total
            weights[key] = round(0.5 + success_rate, 2)

    save_json(WEIGHTS_FILE, weights)


def run_simulation(recent_events: Optional[List[Dict[str, Any]]] = None):
    evaluate_predictions()

    history = get_recent_prices(120)
    if len(history) < 20:
        return

    prices = [x.get('price') for x in history if isinstance(x.get('price'), (int, float))]
    volumes = [x.get('volume', 0) for x in history]
    timestamps = [x.get('timestamp', 0) for x in history]

    if len(prices) < 12:
        return

    pattern = detect_chart_pattern(history)
    direction = "long" if prices[-1] > prices[-12] else "short"
    trend = None
    current_time = int(time.time())

    try:
        win_rate, ma5, ma20, ma60 = calculate_probability(
            prices, timestamps, pattern, trend, direction,
            events=recent_events or [], current_time=current_time,
            volumes=volumes
        )
    except Exception as e:
        print("Error in calculate_probability:", e)
        traceback.print_exc()
        return

    entry = prices[-1]
    stop_loss = entry * (0.98 if direction == "long" else 1.02)
    take_profit = entry * (1.02 if direction == "long" else 0.98)

    try:
        message = f"""📊 *시뮬레이션 결과*

*방향:* {direction.capitalize()}
*진입가:* {entry:.2f}
*손절가:* {stop_loss:.2f}
*익절가:* {take_profit:.2f}
*이동평균:* ma5={f"{ma5:.2f}" if ma5 else 'N/A'}, ma20={f"{ma20:.2f}" if ma20 else 'N/A'}, ma60={f"{ma60:.2f}" if ma60 else 'N/A'}
*패턴:* {pattern or '없음'}
*예상 승률:* {win_rate * 100:.1f}%
"""
        send_telegram_message(message)
    except Exception:
        traceback.print_exc()

    prediction = {
        "timestamp": current_time,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "pattern": pattern,
        "trend": trend,
        "win_rate": win_rate,
        "result": None
    }
    save_prediction(prediction)


def simulate_entry(price_slice: List[Dict[str, Any]], current_price: float, simulate_mode: bool = False, recent_events: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    if len(price_slice) < 20:
        return None

    prices, volumes, timestamps = [], [], []
    for x in price_slice:
        try:
            prices.append(float(x.get('close')))
            volumes.append(float(x.get('volume', 0)))
            timestamps.append(int(x.get('timestamp', 0)))
        except (TypeError, ValueError):
            continue

    if len(prices) < 12:
        return None

    pattern = detect_chart_pattern(price_slice)
    direction = "long" if prices[-1] > prices[-12] else "short"
    trend = None
    current_time = int(time.time())

    try:
        win_rate, ma5, ma20, ma60 = calculate_probability(
            prices, timestamps, pattern, trend, direction,
            events=recent_events or [], current_time=current_time,
            volumes=volumes
        )
    except Exception as e:
        print("Error in calculate_probability:", e)
        traceback.print_exc()
        return None

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
        "ma60": ma60,
        "result": None
    }

    if simulate_mode:
        print("🔍 시뮬레이션 (simulate_mode=True):", result)

    data = load_json(SIMULATION_RESULTS_FILE, [])
    data.append(result)
    save_json(SIMULATION_RESULTS_FILE, data, limit=500)
    save_prediction(result)

    return result


