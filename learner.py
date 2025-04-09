import json
import os
from collections import defaultdict

LOG_FILE = "simulation_log.json"
STATS_FILE = "learning_stats.json"

def analyze_simulation_logs():
    if not os.path.exists(LOG_FILE):
        return

    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except Exception as e:
        print(f"[ERROR] Cannot read simulation log: {e}")
        return

    stats = {
        "patterns": defaultdict(lambda: {"success": 0, "fail": 0}),
        "trend": {"up": {"success": 0, "fail": 0}, "down": {"success": 0, "fail": 0}},
        "direction": {"long": {"success": 0, "fail": 0}, "short": {"success": 0, "fail": 0}},
    }

    for log in logs:
        if not log.get("evaluated") or log.get("result") not in ["success", "fail"]:
            continue

        result = log["result"]
        direction = log["direction"]
        pattern = log.get("pattern")
        ma = log.get("moving_averages", {})
        trend = None

        if ma:
            if ma["ma5"] > ma["ma20"] > ma["ma60"]:
                trend = "up"
            elif ma["ma5"] < ma["ma20"] < ma["ma60"]:
                trend = "down"

        # 방향 성공률
        stats["direction"][direction][result] += 1

        # 패턴별 성공률
        if pattern:
            stats["patterns"][pattern][result] += 1

        # 추세 성공률
        if trend:
            stats["trend"][trend][result] += 1

    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Cannot write stats file: {e}")
