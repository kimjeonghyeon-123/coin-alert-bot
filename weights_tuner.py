import json
import os

PATTERN_STATS_FILE = "pattern_stats.json"
WEIGHTS_FILE = "weights.json"
MIN_WEIGHT = 0.1
MAX_WEIGHT = 2.0


def load_pattern_stats():
    if os.path.exists(PATTERN_STATS_FILE):
        with open(PATTERN_STATS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_weights(weights):
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(weights, f, indent=4)


def tune_weights():
    pattern_stats = load_pattern_stats()
    weights = {}

    for pattern, results in pattern_stats.items():
        if len(results) < 10:
            weight = 1.0  # 데이터 부족 시 기본값
        else:
            success_rate = sum(results) / len(results)
            weight = success_rate * 2.0  # 최대 가중치 2.0 기준

        # 가중치 제한 범위 적용
        weight = max(MIN_WEIGHT, min(MAX_WEIGHT, weight))
        weights[pattern] = round(weight, 2)

    save_weights(weights)
    print("✅ 패턴 가중치 업데이트 완료:", weights)


if __name__ == "__main__":
    tune_weights()
