import json
import os
import time
from datetime import datetime, timedelta
import requests

from price_fetcher import get_current_price
from learning_updater import update_learning_data_from_event
from event_impact_estimator import estimate_next_direction, estimate_impact_duration
from notifier import send_telegram_message

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

def fetch_latest_cpi():
    api_key = "4c660d85c6caa3480c4dd60c1e2fa823"  # 여기에 받은 API 키를 넣으세요.
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 상태 코드가 200이 아닐 경우 예외를 발생시킴
        data = response.json()

        if 'observations' in data and data['observations']:
            # 가장 최근 CPI 값 가져오기
            latest_observation = data['observations'][-1]
            if 'value' in latest_observation:
                return {
                    "time": latest_observation['date'],
                    "actual": float(latest_observation['value'])
                }
            else:
                print("❌ CPI 데이터 값이 없음.")
        else:
            print("❌ CPI 데이터가 없음.")
    except Exception as e:
        print(f"❌ CPI 데이터 수집 오류: {e}")
    return None

def is_already_logged(event_time):
    log = load_json(CPI_EVENT_LOG)
    return any(entry["event_time"] == event_time for entry in log.values())

def log_cpi_event(event_time, expected_cpi, actual_cpi):
    diff = actual_cpi - expected_cpi
    direction = "hot" if diff > 0 else "cool" if diff < 0 else "inline"
    entry_price = get_current_price()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log = load_json(CPI_EVENT_LOG)
    log[timestamp] = {
        "event_time": event_time,
        "expected_cpi": expected_cpi,
        "actual_cpi": actual_cpi,
        "diff": diff,
        "direction": direction,
        "btc_price_at_announcement": entry_price
    }
    save_json(CPI_EVENT_LOG, log)
    print(f"[✅ CPI 기록됨] 예상: {expected_cpi} / 실제: {actual_cpi} / BTC: {entry_price}")

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

    start_price = prices[0][1]
    end_price = prices[-1][1]
    change_percent = ((end_price - start_price) / start_price) * 100

    print(f"📊 CPI 반응 분석: {duration_min}분 동안 {change_percent:.2f}% 변화")
    return change_percent

def auto_process_cpi_event():
    cpi_data = fetch_latest_cpi()
    if not cpi_data:
        print("❌ CPI 데이터 없음. 처리 중지.")
        return

    event_time = cpi_data["time"]
    expected = cpi_data.get("expected")
    actual = cpi_data.get("actual")

    if expected is None or actual is None:
        print("❌ 예상 CPI 값 또는 실제 CPI 값이 없음. 처리 중지.")
        return

    # 이미 기록된 CPI인지 확인
    if is_already_logged(event_time):
        print("⚠️ 이미 기록된 CPI 이벤트입니다. 무시합니다.")
        return

    direction, ts = log_cpi_event(event_time, expected, actual)
    estimated_duration = estimate_impact_duration("CPI", direction)
    change = analyze_cpi_reaction(ts, duration_min=estimated_duration)

    if change is not None:
        update_learning_data_from_event("CPI", direction, change)
        print("🧠 학습 반영 완료")

        try:
            send_telegram_message(f"""📈 *CPI 발표 감지됨!*

*시간:* {event_time}
*예상치:* {expected:.2f}
*실제치:* {actual:.2f}
*방향:* {direction.upper()}
*가격 변화 추정:* {change:.2f}% ({estimated_duration}분 기준)
            """)
        except Exception as e:
            print("❌ 텔레그램 메시지 전송 실패:", e)

# 향후 CPI 예측 요청 시 호출
def predict_next_cpi_reaction():
    prediction = estimate_next_direction("CPI")
    try:
        send_telegram_message(f"🔮 *다음 CPI 발표 예상 방향:* {prediction.upper()}")
    except Exception as e:
        print("❌ 텔레그램 전송 실패 (CPI 예측):", e)
    return prediction

def get_latest_cpi_direction():
    """
    최신 CPI 데이터를 불러와서 방향(hot/cool/inline)을 반환하는 함수
    """
    data = fetch_latest_cpi()
    if not data:
        return "neutral"
    return estimate_next_direction({
        "type": "CPI",
        "value": data["actual"],
        "forecast": data["expected"]
    })
