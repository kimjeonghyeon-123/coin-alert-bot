import json
import os

PATTERN_STATS_FILE = "pattern_stats.json"
MIN_SAMPLES = 10
MIN_SUCCESS_RATE = 0.75

def load_stats():
    if os.path.exists(PATTERN_STATS_FILE):
        with open(PATTERN_STATS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(PATTERN_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def update_pattern_stats(prediction, result):
    stats = load_stats()
    for pattern in prediction.get("used_patterns", []):
        if pattern not in stats:
            stats[pattern] = []

        stats[pattern].append(1 if result == "success" else 0)
        stats[pattern] = stats[pattern][-50:]  # 최근 50개만 유지

    save_stats(stats)

def get_valid_patterns():
    stats = load_stats()
    valid_patterns = []
    for pattern, results in stats.items():
        if len(results) >= MIN_SAMPLES:
            rate = sum(results) / len(results)
            if rate >= MIN_SUCCESS_RATE:
                valid_patterns.append((pattern, round(rate, 3)))
    return valid_patterns
