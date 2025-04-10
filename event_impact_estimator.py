import json
import os

STATS_FILE = "learning_stats.json"

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def estimate_cpi_impact(direction):
    stats = load_json(STATS_FILE)

    if "CPI" not in stats or direction not in stats["CPI"]:
        return {
            "direction": direction,
            "known": False,
            "message": f"CPI 방향 '{direction}'에 대한 학습된 데이터가 부족합니다."
        }

    cpi_stat = stats["CPI"][direction]
    avg_change = cpi_stat["average_change"]
    count = cpi_stat["count"]
    pos = cpi_stat["positive_count"]
    neg = cpi_stat["negative_count"]

    bias = "상승 우세" if avg_change > 0 else "하락 우세"
    prob = round((pos / count) * 100, 1) if count > 0 else 0

    return {
        "direction": direction,
        "known": True,
        "average_change_percent": round(avg_change, 3),
        "positive_rate_percent": prob,
        "bias": bias,
        "message": f"CPI '{direction}' 발생 시 평균 변화율은 {avg_change:.2f}%. {bias} 경향이며, {prob}% 확률로 상승."
    }

# 예시 실행
if __name__ == "__main__":
    for d in ["hot", "cool", "inline"]:
        result = estimate_cpi_impact(d)
        print(f"[📊 {d.upper()} 예측] {result['message']}")
