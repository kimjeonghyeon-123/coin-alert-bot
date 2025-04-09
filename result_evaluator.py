import json
import os

PATTERN_STATS_FILE = "pattern_stats.json"
MAX_RECENT_RESULTS = 50


def load_pattern_stats():
    if os.path.exists(PATTERN_STATS_FILE):
        with open(PATTERN_STATS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_pattern_stats(stats):
    with open(PATTERN_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)


def evaluate_simulation(prediction, actual_result):
    pattern_stats = load_pattern_stats()
    for pattern in prediction.get("used_patterns", []):
        if pattern not in pattern_stats:
            pattern_stats[pattern] = []

        result = 1 if actual_result == "success" else 0
        pattern_stats[pattern].append(result)

        if len(pattern_stats[pattern]) > MAX_RECENT_RESULTS:
            pattern_stats[pattern] = pattern_stats[pattern][-MAX_RECENT_RESULTS:]

    save_pattern_stats(pattern_stats)


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
