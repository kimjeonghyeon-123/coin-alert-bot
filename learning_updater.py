import json
import os
import time

STATS_FILE = "learning_stats.json"
RESULT_LOG = "simulation_results.json"
UPDATE_INTERVAL = 60  # 몇 초마다 자동 업데이트할지 설정 (예: 60초)

def load_json(path):
    # 파일이 없으면 자동으로 빈 JSON 생성
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def update_stats_from_results():
    stats = load_json(STATS_FILE)
    results = load_json(RESULT_LOG)

    # 필요한 섹션이 없으면 초기화
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

        # 결과 평가
        success = False
        if direction == "long":
            success = result_price >= take_profit
        elif direction == "short":
            success = result_price <= take_profit

        # 통계 업데이트 함수
        def update_category(category, key, success):
            if key not in stats[category]:
                stats[category][key] = {"success": 0, "fail": 0}
            stats[category][key]["success" if success else "fail"] += 1

        if pattern:
            update_category("patterns", pattern, success)
        if trend:
            update_category("trend", trend, success)
        update_category("direction", direction, success)

        # 이벤트 지속 시간 학습
        if event:
            ekey = event.get("type", "") + "_" + event.get("source", "")
            duration = event.get("duration", 3600)
            if ekey not in stats["event_durations"]:
                stats["event_durations"][ekey] = {"total": 0, "count": 0}
            stats["event_durations"][ekey]["total"] += duration
            stats["event_durations"][ekey]["count"] += 1

        # 결과 평가 완료 표시
        r["evaluated"] = True
        new_results.append(r)
        updated = True

    if updated:
        save_json(STATS_FILE, stats)
        save_json(RESULT_LOG, {"logs": new_results})
        print("[✅ 업데이트 완료] 학습 통계 및 결과 반영됨.")
    else:
        print("[⏸ 대기 중] 새로운 평가할 결과 없음.")

if __name__ == "__main__":
    print("🔁 자동 학습 업데이트 시작...")
    while True:
        update_stats_from_results()
        time.sleep(UPDATE_INTERVAL)

