import json
import os
from collections import defaultdict

LOG_FILE = "simulation_log.json"
STATS_FILE = "learning_stats.json"

def analyze_simulation_logs():
    if not os.path.exists(LOG_FILE):
        print(f"[INFO] No simulation log found at {LOG_FILE}")
        return

    # 시뮬레이션 로그 로딩
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

    # 로그 분석
    for log in logs:
        if not log.get("evaluated") or log.get("result") not in ["success", "fail"]:
            continue

        result = log["result"]
        direction = log.get("direction")
        pattern = log.get("pattern")
        ma = log.get("moving_averages", {})

        # 유효한 방향만 기록
        if direction in stats["direction"]:
            stats["direction"][direction][result] += 1

        # 패턴 성공률 기록
        if pattern:
            stats["patterns"][pattern][result] += 1

        # 추세 방향 분석
        trend = None
        try:
            if ma["ma5"] > ma["ma20"] > ma["ma60"]:
                trend = "up"
            elif ma["ma5"] < ma["ma20"] < ma["ma60"]:
                trend = "down"
        except KeyError:
            pass

        if trend:
            stats["trend"][trend][result] += 1

    # 결과 저장
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"[INFO] Learning stats saved to {STATS_FILE}")
    except Exception as e:
        print(f"[ERROR] Cannot write stats file: {e}")
