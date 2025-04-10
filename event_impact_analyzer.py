import json
import os
from datetime import datetime
from price_logger import load_price_data

EVENT_IMPACT_LOG = "event_impact_log.json"
MIN_IMPACT_THRESHOLD = 0.005  # 0.5% 이상 움직임이 의미 있다고 판단

def estimate_price_impact(event_time, event_type, description, max_check_hours=6):
    try:
        price_data = load_price_data()
    except Exception as e:
        print(f"[오류] 가격 데이터 로드 실패: {e}")
        return None

    event_ts = int(datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S").timestamp())
    if str(event_ts) not in price_data:
        print("[오류] 이벤트 시간 가격 정보 없음")
        return None

    initial_price = float(price_data[str(event_ts)])
    max_ts = event_ts + max_check_hours * 3600

    timestamps = sorted(int(ts) for ts in price_data if event_ts <= int(ts) <= max_ts)
    if not timestamps:
        print("[오류] 분석 가능한 시간대 데이터 부족")
        return None

    max_price = initial_price
    min_price = initial_price
    last_significant_ts = event_ts

    for ts in timestamps:
        price = float(price_data[str(ts)])
        max_price = max(max_price, price)
        min_price = min(min_price, price)

        change_up = (max_price - initial_price) / initial_price
        change_down = (initial_price - min_price) / initial_price

        if change_up >= MIN_IMPACT_THRESHOLD or change_down >= MIN_IMPACT_THRESHOLD:
            last_significant_ts = ts
        else:
            break  # 의미 있는 움직임 없으면 종료

    duration_sec = last_significant_ts - event_ts
    duration_hr = round(duration_sec / 3600, 2)

    impact = {
        "event_time": event_time,
        "type": event_type,
        "description": description,
        "initial_price": initial_price,
        "max_price": round(max_price, 2),
        "min_price": round(min_price, 2),
        "up_move_pct": round((max_price - initial_price) / initial_price * 100, 2),
        "down_move_pct": round((initial_price - min_price) / initial_price * 100, 2),
        "impact_duration_hr": duration_hr
    }

    save_impact(impact)
    return impact

def save_impact(impact):
    impacts = []
    if os.path.exists(EVENT_IMPACT_LOG):
        with open(EVENT_IMPACT_LOG, 'r') as f:
            try:
                impacts = json.load(f)
            except:
                impacts = []

    # 중복 저장 방지
    for i in impacts:
        if i["event_time"] == impact["event_time"] and i["description"] == impact["description"]:
            return

    impacts.append(impact)
    with open(EVENT_IMPACT_LOG, 'w') as f:
        json.dump(impacts, f, indent=2)

def get_average_impact_duration():
    if not os.path.exists(EVENT_IMPACT_LOG):
        return 1.0

    with open(EVENT_IMPACT_LOG, 'r') as f:
        data = json.load(f)

    durations = [item["impact_duration_hr"] for item in data if "impact_duration_hr" in item]
    if not durations:
        return 1.0

    return round(sum(durations) / len(durations), 2)

if __name__ == "__main__":
    test_event_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    impact = estimate_price_impact(test_event_time, "macro", "FOMC 발표")
    print(impact)

    avg_dur = get_average_impact_duration()
    print(f"📊 평균 영향 지속 시간: {avg_dur}시간")

