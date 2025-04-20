import json
import os
from datetime import datetime, timedelta

from price_fetcher import get_price_and_volume
from learning_updater import update_learning_data_from_event
from event_impact_estimator import estimate_next_direction, estimate_impact_duration
from notifier import send_telegram_message
from multi_country_cpi_fetcher import fetch_latest_cpis  # ✅ 다국가 CPI fetcher

CPI_EVENT_LOG = "cpi_event_log.json"
BTC_PRICE_LOG = "btc_price_log.json"

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ {path} 파일을 읽을 수 없습니다. JSON 형식이 잘못되었을 수 있습니다.")
        return {}
    except Exception as e:
        print(f"❌ {path} 파일 로드 중 오류: {e}")
        return {}

def is_already_logged(country, event_time):
    log = load_json(CPI_EVENT_LOG)
    return any(entry["country"] == country and entry["event_time"] == event_time for entry in log.values())

def log_cpi_event(country, event_time, expected_cpi, actual_cpi):
    diff = actual_cpi - expected_cpi
    direction = "hot" if diff > 0 else "cool" if diff < 0 else "inline"
    entry_price, entry_volume = get_price_and_volume()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log = load_json(CPI_EVENT_LOG)
    log[timestamp] = {
        "country": country,
        "event_time": event_time,
        "expected_cpi": expected_cpi,
        "actual_cpi": actual_cpi,
        "diff": diff,
        "direction": direction,
        "btc_price_at_announcement": entry_price,
        "volume_at_announcement": entry_volume
    }
    save_json(CPI_EVENT_LOG, log)
    print(f"[✅ {country} CPI 기록됨] 예상: {expected_cpi} / 실제: {actual_cpi} / BTC: {entry_price} / 거래량: {entry_volume}")

    return direction, timestamp

def analyze_cpi_reaction(cpi_time_str, duration_min=60):
    price_log = load_json(BTC_PRICE_LOG)
    cpi_time = datetime.strptime(cpi_time_str, "%Y-%m-%d %H:%M:%S")

    prices = []
    for ts, price in price_log.items():
        try:
            t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            if cpi_time <= t <= cpi_time + timedelta(minutes=duration_min):
                prices.append((t, price))
        except Exception:
            continue

    if not prices:
        print("📭 해당 시간대 가격 데이터 없음.")
        return None

    start_price = prices[0][1][0]  # 가격
    end_price = prices[-1][1][0]
    start_volume = prices[0][1][1]  # 거래량
    avg_volume = sum([p[1][1] for p in prices]) / len(prices)

    change_percent = ((end_price - start_price) / start_price) * 100

    print(f"📊 CPI 반응 분석: {duration_min}분 동안 {change_percent:.2f}% 변화 / 평균 거래량: {avg_volume:.2f}")
    return change_percent

def auto_process_cpi_events():
    cpi_list = fetch_latest_cpis()
    if not cpi_list:
        print("❌ CPI 데이터 없음. 처리 중지.")
        return

    for item in cpi_list:
        country = item.get("country")
        event_time = item.get("time")
        expected = item.get("expected")
        actual = item.get("actual")

        if country is None or event_time is None:
            print("❌ 필수 CPI 항목 누락됨. 스킵.")
            continue

        if expected is None or actual is None:
            print(f"❌ {country} 예상 또는 실제 CPI 없음. 스킵.")
            continue

        if is_already_logged(country, event_time):
            print(f"⚠️ {country} CPI 이미 기록됨. 무시.")
            continue

        direction, ts = log_cpi_event(country, event_time, expected, actual)
        estimated_duration = estimate_impact_duration("CPI", direction)
        change = analyze_cpi_reaction(ts, duration_min=estimated_duration)

        if change is not None:
            update_learning_data_from_event("CPI", direction, change)
            print(f"🧠 {country} CPI 학습 반영 완료")

            try:
                send_telegram_message(f"""📈 *{country} CPI 발표 감지됨!*

*시간:* {event_time}
*예상치:* {expected:.2f}
*실제치:* {actual:.2f}
*방향:* {direction.upper()}
*가격 변화 추정:* {change:.2f}% ({estimated_duration}분 기준)
                """)
            except Exception as e:
                print(f"❌ 텔레그램 메시지 전송 실패 ({country} CPI):", e)

def predict_next_cpi_reaction(country="United States"):
    prediction = estimate_next_direction("CPI")
    try:
        send_telegram_message(f"🔮 *다음 {country} CPI 발표 예상 방향:* {prediction.upper()}")
    except Exception as e:
        print(f"❌ 텔레그램 전송 실패 (CPI 예측):", e)
    return prediction

def get_latest_cpi_direction(country="United States"):
    try:
        cpi_list = fetch_latest_cpis()
        for item in cpi_list:
            if item.get("country") == country:
                actual = item.get("actual")
                expected = item.get("expected")
                if actual is None or expected is None:
                    print(f"[CPI 경고] {country} 데이터 누락됨.")
                    return "neutral"
                return estimate_next_direction({
                    "type": "CPI",
                    "value": actual,
                    "forecast": expected
                })
        print(f"[CPI] {country} CPI 데이터 없음.")
        return "neutral"
    except Exception as e:
        print(f"[CPI 오류] {country} 방향 추정 실패: {e}")
        return "neutral"

def get_latest_all_cpi_directions():
    """✅ entry_angle_detector.py에서 import하는 함수"""
    result = {}
    try:
        cpi_list = fetch_latest_cpis()
        for item in cpi_list:
            country = item.get("country")
            actual = item.get("actual")
            expected = item.get("expected")
            if country and actual is not None and expected is not None:
                result[country] = estimate_next_direction({
                    "type": "CPI",
                    "value": actual,
                    "forecast": expected
                })
            else:
                result[country] = "neutral"
    except Exception as e:
        print(f"❌ get_latest_all_cpi_directions 오류: {e}")
    return result



