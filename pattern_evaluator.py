import json
import os

PATTERN_STATS_FILE = "pattern_stats.json"
MAX_RECENT_RESULTS = 50
MIN_SUCCESS_RATE = 0.3  # 이 값 이하의 성공률은 '비신뢰 패턴'으로 판단

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
            pattern_stats[pattern] = {
                "results": [],
                "recent_success_rate": 0.0,
                "total_success": 0,
                "total_fail": 0
            }

        result = 1 if actual_result == "success" else 0
        pattern_stats[pattern]["results"].append(result)

        # 최근 결과 유지
        if len(pattern_stats[pattern]["results"]) > MAX_RECENT_RESULTS:
            pattern_stats[pattern]["results"] = pattern_stats[pattern]["results"][-MAX_RECENT_RESULTS:]

        # 성공/실패 카운팅
        if result:
            pattern_stats[pattern]["total_success"] += 1
        else:
            pattern_stats[pattern]["total_fail"] += 1

        # 최근 성공률 계산
        recent = pattern_stats[pattern]["results"]
        pattern_stats[pattern]["recent_success_rate"] = round(sum(recent) / len(recent), 2)

        # 경고 출력
        if pattern_stats[pattern]["recent_success_rate"] < MIN_SUCCESS_RATE:
            print(f"[⚠️ LOW SUCCESS RATE] Pattern '{pattern}' has recent success rate of {pattern_stats[pattern]['recent_success_rate']*100:.1f}%")

    save_pattern_stats(pattern_stats)
