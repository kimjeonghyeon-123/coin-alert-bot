import json
import time
import os
from price_logger import get_current_price

PATTERN_STATS_FILE = "pattern_stats.json"
SIMULATION_FILE = "simulation_results.json"
MAX_RECENT_RESULTS = 50
EVALUATION_DELAY = 1800  # 30분

# 패턴별 성공/실패 기록 로딩
def load_pattern_stats():
    if os.path.exists(PATTERN_STATS_FILE):
        with open(PATTERN_STATS_FILE, "r") as f:
            return json.load(f)
    return {}

# 패턴별 성공/실패 저장
def save_pattern_stats(stats):
    with open(PATTERN_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

# 패턴별 평가 후 저장
def evaluate_simulation(prediction, actual_result):
    pattern_stats = load_pattern_stats()

    # 패턴 정보 추출 (단일 or 리스트 처리)
    patterns = prediction.get("used_patterns") or [prediction.get("pattern", "none")]
    for pattern in patterns:
        if pattern not in pattern_stats:
            pattern_stats[pattern] = []
        result = 1 if actual_result == "success" else 0
        pattern_stats[pattern].append(result)

        # 최대 최근 결과 수 제한
        if len(pattern_stats[pattern]) > MAX_RECENT_RESULTS:
            pattern_stats[pattern] = pattern_stats[pattern][-MAX_RECENT_RESULTS:]

    save_pattern_stats(pattern_stats)

# 기준 이상 성능 보이는 패턴만 반환
def get_valid_patterns():
    stats = load_pattern_stats()
    valid_patterns = []

    for pattern, results in stats.items():
        if len(results) < 10:
            valid_patterns.append(pattern)
            continue
        fail_rate = results.count(0) / len(results)
        if fail_rate < 0.6:
            valid_patterns.append(pattern)

    return valid_patterns

# 메인 평가 로직
def evaluate_predictions():
    try:
        with open(SIMULATION_FILE, "r") as f:
            predictions = json.load(f)
    except:
        return

    now = int(time.time())
    updated_predictions = []

    for pred in predictions:
        if now - pred["timestamp"] < EVALUATION_DELAY:
            updated_predictions.append(pred)
            continue

        current_price = get_current_price()
        direction = pred["direction"]
        success = None

        if direction == "long":
            if current_price >= pred["take_profit"]:
                success = True
            elif current_price <= pred["stop_loss"]:
                success = False
            else:
                updated_predictions.append(pred)
                continue
        else:  # short
            if current_price <= pred["take_profit"]:
                success = True
            elif current_price >= pred["stop_loss"]:
                success = False
            else:
                updated_predictions.append(pred)
                continue

        result = "success" if success else "fail"
        evaluate_simulation(pred, result)

    with open(SIMULATION_FILE, "w") as f:
        json.dump(updated_predictions, f, indent=2)

if __name__ == "__main__":
    evaluate_predictions()

