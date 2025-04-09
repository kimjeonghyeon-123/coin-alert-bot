# simulation_evaluator.py
import json
import time
import os

LOG_FILE = "simulation_log.json"
LEARN_FILE = "learning_stats.json"

def load_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r') as f:
        return json.load(f)

def save_logs(logs):
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def update_learning(stats, key_type, key, success):
    if key_type not in stats:
        stats[key_type] = {}
    if key not in stats[key_type]:
        stats[key_type][key] = {"success": 0, "fail": 0}
    stats[key_type][key]["success" if success else "fail"] += 1

def evaluate_simulations():
    logs = load_logs()
    updated = False

    try:
        with open(LEARN_FILE, 'r') as f:
            stats = json.load(f)
    except:
        stats = {}

    for log in logs:
        if log["evaluated"]:
            continue

        timestamp = int(time.mktime(time.strptime(log["timestamp"], "%Y-%m-%dT%H:%M:%S")))
        direction = log["direction"]
        entry_price = log["entry_price"]
        stop_loss = log["stop_loss"]
        take_profit = log["take_profit"]

        # 최근 15분간의 가격 데이터를 불러와서 비교 (가장 단순한 예시)
        # 예: price_logger로부터 5분 간격 3개
        from price_logger import get_recent_prices
        recent = get_recent_prices(3)  # 15분치
        if not recent:
            continue
        future_prices = [p['price'] for p in recent]
        hit_tp = any(p >= take_profit if direction == "Long" else p <= take_profit for p in future_prices)
        hit_sl = any(p <= stop_loss if direction == "Long" else p >= stop_loss for p in future_prices)

        # 평가
        if hit_tp and not hit_sl:
            result = "success"
            success = True
        elif hit_sl and not hit_tp:
            result = "fail"
            success = False
        else:
            # TP/SL 동시에 닿았거나 닿지 않음 (무효 처리)
            continue

        # 학습 반영
        update_learning(stats, "direction", direction.lower(), success)
        if log.get("pattern"):
            update_learning(stats, "patterns", log["pattern"], success)
        if log.get("moving_averages"):
            ma = log["moving_averages"]
            if ma["ma5"] > ma["ma20"] > ma["ma60"]:
                update_learning(stats, "trend", "up", success)
            elif ma["ma5"] < ma["ma20"] < ma["ma60"]:
                update_learning(stats, "trend", "down", success)

        # 로그에도 업데이트
        log["evaluated"] = True
        log["result"] = result
        updated = True

    if updated:
        save_logs(logs)
        with open(LEARN_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
