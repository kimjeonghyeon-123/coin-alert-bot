import json
import os
import time
from datetime import datetime

STATS_FILE = "learning_stats.json"
RESULT_LOG = "simulation_results.json"
CPI_LOG = "cpi_event_log.json"
UPDATE_INTERVAL = 60  # 초 단위 자동 업데이트 주기

def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def update_category(stats, category, key, success):
    if key not in stats[category]:
        stats[category][key] = {"success": 0, "fail": 0}
    stats[category][key]["success" if success else "fail"] += 1

def update_cpi_learning():
    stats = load_json(STATS_FILE)
    cpi_logs = load_json(CPI_LOG)

    if "CPI" not in stats:
        stats["CPI"] = {}

    updated = False

    for ts, cpi_event in cpi_logs.items():
        if cpi_event.get("evaluated"):
            continue

        direction = cpi_event["direction"]  # 'hot', 'cool', 'inline'
        before_price = cpi_event["btc_price_at_announcement"]
        after_price = cpi_event.get("btc_price_after_duration")

        if after_price is None:
            continue  # 아직 가격 변화가 기록되지 않음

        change_percent = ((after_price - before_price) / before_price) * 100

        if direction not in stats["CPI"]:
            stats["CPI"][direction] = {
                "count": 0,
                "total_change": 0.0,
                "average_change": 0.0,
                "positive_count": 0,
                "negative_count": 0
            }

        d_stat = stats["CPI"][direction]
        d_stat["count"] += 1
        d_stat["total_change"] += change_percent
        d_stat["average_change"] = d_stat["total_change"] / d_stat["count"]
        if change_percent > 0:
            d_stat["positive_count"] += 1
        elif change_percent < 0:
            d_stat["negative_count"] += 1

        cpi_event["evaluated"] = True
        cpi_logs[ts] = cpi_event
        updated = True

    if updated:
        save_json(CPI_LOG, cpi_logs)
        save_json(STATS_FILE, stats)
        print("📊 CPI 학습 데이터 업데이트 완료")

def update_simulation_results():
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
        trend = r.get("trend")
        entry_price = r["entry_price"]
        stop_loss = r["stop_loss"]
        take_profit = r["take_profit"]
        result_price = r["result_price"]
        event = r.get("event")

        success = False
        if direction == "long":
            success = result_price >= take_profit
        elif direction == "short":
            success = result_price <= take_profit

        if pattern:
            update_category(stats, "patterns", pattern, success)
        if trend:
            update_category(stats, "trend", trend, success)
        update_category(stats, "direction", direction, success)

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
        print("📈 시뮬레이션 결과 학습 완료")
    else:
        print("⏸️ 시뮬레이션에 학습할 새 데이터 없음.")

if __name__ == "__main__":
    print("🔁 자동 학습 시스템 가동 중...")
    while True:
        update_simulation_results()
        update_cpi_learning()
        time.sleep(UPDATE_INTERVAL)


