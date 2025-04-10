import json
import os

PATTERN_STATS_FILE = "pattern_stats.json"
MAX_RECENT_RESULTS = 50
MIN_SUCCESS_RATE = 0.3  # 이 값 이하의 성공률은 '비신뢰 패턴'으로 판단

def load_pattern_stats():
    if os.path.exists(PATTERN_STATS_FILE):
        try:
            with open(PATTERN_STATS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[오류] 패턴 통계 파일이 손상되어 초기화됩니다.")
            return {}
    return {}

def save_pattern_stats(stats):
    with open(PATTERN_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def evaluate_simulation(prediction, actual_result):
    pattern_stats = load_pattern_stats()
    used_patterns = prediction.get("used_patterns", [])

    result = 1 if actual_result == "success" else 0

    for pattern in used_patterns:
        stats = pattern_stats.setdefault(pattern, {
            "results": [],
            "recent_success_rate": 0.0,
            "total_success": 0,
            "total_fail": 0,
        })

        stats["results"].append(result)

        # 최근 결과만 유지
        if len(stats["results"]) > MAX_RECENT_RESULTS:
            stats["results"] = stats["results"][-MAX_RECENT_RESULTS:]

        if result:
            stats["total_success"] += 1
        else:
            stats["total_fail"] += 1

        # 최근 성공률 업데이트
        stats["recent_success_rate"] = round(sum(stats["results"]) / len(stats["results"]), 2)

        if stats["recent_success_rate"] < MIN_SUCCESS_RATE:
            print(f"[⚠️ LOW SUCCESS RATE] Pattern '{pattern}' 성공률: {stats['recent_success_rate']*100:.1f}%")

    save_pattern_stats(pattern_stats)

