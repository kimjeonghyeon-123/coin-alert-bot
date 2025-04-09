import json
import time
import os

LOG_FILE = "simulation_log.json"
PRICE_HISTORY_FILE = "price_history.json"  # price_logger가 쓰는 파일

PENALIZE_PATTERNS = {}


def evaluate_simulation_results():
    if not os.path.exists(LOG_FILE) or not os.path.exists(PRICE_HISTORY_FILE):
        return

    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)

    with open(PRICE_HISTORY_FILE, 'r') as f:
        price_data = json.load(f)

    updated = False
    for entry in logs:
        if entry["evaluated"]:
            continue

        timestamp = entry["timestamp"]
        entry_price = entry["entry_price"]
        direction = entry["direction"]
        tp = entry["take_profit"]
        sl = entry["stop_loss"]
        pattern = entry.get("pattern")

        # 평가 기준: entry 이후의 가격 흐름
        matched_result = None
        for p in price_data:
            if p["timestamp"] > timestamp:
                price = p["price"]
                if direction == "long" and price >= tp:
                    matched_result = "win"
                    break
                elif direction == "long" and price <= sl:
                    matched_result = "lose"
                    break
                elif direction == "short" and price <= tp:
                    matched_result = "win"
                    break
                elif direction == "short" and price >= sl:
                    matched_result = "lose"
                    break

        if matched_result:
            entry["evaluated"] = True
            entry["result"] = matched_result
            updated = True

            # 패턴 패널티 반영
            if matched_result == "lose" and pattern:
                PENALIZE_PATTERNS[pattern] = PENALIZE_PATTERNS.get(pattern, 0) + 1

    if updated:
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

    return PENALIZE_PATTERNS


def get_penalized_patterns():
    return PENALIZE_PATTERNS
