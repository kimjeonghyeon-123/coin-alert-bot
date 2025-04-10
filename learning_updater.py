import json
import os
import time

STATS_FILE = "learning_stats.json"
RESULT_LOG = "simulation_results.json"

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def update_stats_from_results():
    stats = load_json(STATS_FILE)
    results = load_json(RESULT_LOG)

    if "patterns" not in stats:
        stats["patterns"] = {}
    if "direction" not in stats:
        stats["direction"] = {}
    if "trend" not in stats:
        stats["trend"] = {}
    if "event_durations" not in stats:
        stats["event_durations"] = {}

    updated = False
    new_results = []

    for r in results.get("logs", []):
        if r.get("evaluated"):
            new_results.append(r)
            continue

        direction = r["direction"]
        pattern = r["pattern"]
        trend = r.get("trend", None)
        entry_price = r["entry_price"]
        stop_loss = r["stop_loss"]
        take_profit = r["take_profit"]
        result_price = r["result_price"]
        event = r.get("event")

        success = False
        if direction == "long":
            if result_price >= take_profit:
                success = True
            elif result_price <= stop_loss:
                success = False
        elif direction == "short":
            if result_price <= take_profit:
                success = True
            elif result_price >= stop_loss:
                success = False

        def update_category(category, key, success):
            if key not in stats[category]:
                stats[category][key] = {"success": 0, "fail": 0}
            stats[category][key]["success" if success else "fail"] += 1

        if pattern:
            update_category("patterns", pattern, success)
        if trend:
            update_category("trend", trend, success)
        update_category("direction", direction, success)

        # 이벤트 지속 시간 업데이트
        if event:
            ekey = event.get("type", "") + "_" + event.get("source", "")
            duration = event.get("duration", 3600)
            if ekey not in stats["event_durations"]:
                stats["event_durations"][ekey] = {"total": 0, "count": 0}
            stats["event_durations"][ekey]["total"] += duration
            stats["event_durations"][ekey]["count"] += 1

        r["evaluated"] = True
        new_results.append(r)
        updated = True

    if updated:
        save_json(STATS_FILE, stats)
        save_json(RESULT_LOG, {"logs": new_results})
