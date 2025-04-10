import json

def load_learning_stats():
    try:
        with open("learning_stats.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_weights(weights):
    with open("weights.json", "w") as f:
        json.dump(weights, f, indent=4)

def optimize_weights():
    stats = load_learning_stats()

    # 초기 기본값
    weights = {
        "pattern": 0.4,
        "trend": 0.3,
        "direction": 0.3,
        "angle": 0.05,
        "inflection": 0.03,
        "event_high": 0.2,
        "event_medium": 0.1,
        "event_low": 0.05
    }

    # 조정 함수
    def calc_dynamic_weight(data, base_weight, cap=0.6, floor=0.1):
        total = data["success"] + data["fail"]
        if total < 10:
            return base_weight  # 데이터가 적으면 그대로
        winrate = data["success"] / total
        if winrate > 0.6:
            return min(cap, base_weight + (winrate - 0.5))  # 승률 높으면 강화
        elif winrate < 0.4:
            return max(floor, base_weight - (0.5 - winrate))  # 낮으면 약화
        return base_weight

    # 동적으로 계산
    if "patterns" in stats:
        avg = [calc_dynamic_weight(p, 0.4) for p in stats["patterns"].values()]
        if avg:
            weights["pattern"] = round(sum(avg) / len(avg), 3)

    if "trend" in stats and stats["trend"]:
        avg = [calc_dynamic_weight(t, 0.3) for t in stats["trend"].values()]
        if avg:
            weights["trend"] = round(sum(avg) / len(avg), 3)

    if "direction" in stats and stats["direction"]:
        avg = [calc_dynamic_weight(d, 0.3) for d in stats["direction"].values()]
        if avg:
            weights["direction"] = round(sum(avg) / len(avg), 3)

    save_weights(weights)
    print("✅ weights.json 업데이트 완료:", weights)

# 메인 실행
if __name__ == "__main__":
    optimize_weights()
