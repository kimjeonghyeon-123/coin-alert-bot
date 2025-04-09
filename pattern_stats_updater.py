# pattern_stats_updater.py
import json
import os

PATTERN_STATS_FILE = "pattern_stats.json"
TRUSTED_PATTERNS_FILE = "trusted_patterns.json"
MIN_SUCCESS_RATE = 0.7
MIN_ATTEMPTS = 20

def update_trusted_patterns():
    if not os.path.exists(PATTERN_STATS_FILE):
        print("No pattern stats found.")
        return

    with open(PATTERN_STATS_FILE, "r") as f:
        stats = json.load(f)

    trusted_patterns = {}
    for pattern, results in stats.items():
        if len(results) >= MIN_ATTEMPTS:
            success_rate = sum(results) / len(results)
            if success_rate >= MIN_SUCCESS_RATE:
                trusted_patterns[pattern] = round(success_rate, 3)

    with open(TRUSTED_PATTERNS_FILE, "w") as f:
        json.dump(trusted_patterns, f, indent=4)

    print(f"Updated {len(trusted_patterns)} trusted patterns.")

if __name__ == "__main__":
    update_trusted_patterns()
