import json
import os

PATTERN_STATS_FILE = "pattern_stats.json"
TRUSTED_PATTERNS_FILE = "trusted_patterns.json"
MIN_SUCCESS_RATE = 0.7
MIN_ATTEMPTS = 20

def update_trusted_patterns():
    if not os.path.exists(PATTERN_STATS_FILE):
        print("[⚠️ 경고] 패턴 통계 파일이 존재하지 않습니다.")
        return

    with open(PATTERN_STATS_FILE, "r") as f:
        stats = json.load(f)

    trusted_patterns = {}

    for pattern, data in stats.items():
        results = data.get("results", [])
        if not isinstance(results, list):
            continue

        total_attempts = len(results)
        if total_attempts < MIN_ATTEMPTS:
            continue

        success_rate = sum(results) / total_attempts if total_attempts > 0 else 0.0
        if success_rate >= MIN_SUCCESS_RATE:
            trusted_patterns[pattern] = round(success_rate, 3)

    with open(TRUSTED_PATTERNS_FILE, "w") as f:
        json.dump(trusted_patterns, f, indent=4)

    print(f"[✅ 완료] 신뢰 가능한 패턴 {len(trusted_patterns)}개를 업데이트했습니다.")
    if len(trusted_patterns) > 0:
        print(f"📈 신뢰 패턴 목록: {list(trusted_patterns.keys())}")

if __name__ == "__main__":
    update_trusted_patterns()

