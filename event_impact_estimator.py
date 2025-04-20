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

def estimate_next_direction(event):
    """
    CPI 이벤트 데이터를 기반으로 다음 방향성을 추정.
    """
    if event.get("type") == "CPI":
        value = event.get("value")
        forecast = event.get("forecast")
        if value is None or forecast is None:
            return "inline"
        if value > forecast:
            return "hot"
        elif value < forecast:
            return "cool"
        else:
            return "inline"
    return "neutral"

def estimate_impact_duration(event):
    """
    이벤트별 평균 지속시간을 추정 (학습된 통계를 기반으로).
    """
    stats = load_json(STATS_FILE)
    if "event_durations" not in stats:
        return 3600  # 기본 1시간

    key = f"{event.get('type','')}_{event.get('source','')}"
    if key in stats["event_durations"]:
        data = stats["event_durations"][key]
        if data["count"] > 0:
            return int(data["total"] / data["count"])

    return 3600  # 기본값

def estimate_cpi_impact_for_all(cpi_list):
    """
    entry_angle_detector.py에서 사용하는 함수.
    cpi_list = [{country, actual, expected, time}]
    return 예시: {'United States': {'direction': 'hot', 'duration': 3600}, ...}
    """
    result = {}
    for item in cpi_list:
        country = item.get("country")
        actual = item.get("actual")
        expected = item.get("expected")

        if not country or actual is None or expected is None:
            continue

        direction = estimate_next_direction({
            "type": "CPI",
            "value": actual,
            "forecast": expected
        })
        duration = estimate_impact_duration({
            "type": "CPI",
            "source": country
        })

        result[country] = {
            "direction": direction,
            "duration": duration
        }

    return result

# 예시 실행
if __name__ == "__main__":
    for d in ["hot", "cool", "inline"]:
        result = estimate_cpi_impact(d)
        print(f"[📊 {d.upper()} 예측] {result['message']}")


