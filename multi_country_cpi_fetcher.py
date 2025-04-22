import json
import os
import requests
from datetime import datetime

# ✅ 미국 CPI 코드만 유지
COUNTRY_CPI_CODES = {
    "USA": "USA.A.HICP.CPI.IX.CP00.N._Z"
}

CPI_EVENT_LOG = "cpi_event_log.json"


def fetch_latest_cpi_from_dbnomics(country_code):
    series_code = COUNTRY_CPI_CODES[country_code]
    url = f"https://api.db.nomics.world/v22/series/Eurostat/PRC_HICP_MIDX/{series_code}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        observations = data["series"]["docs"][0]["periods"]

        # 최신 데이터 추출
        latest_period = sorted(observations.keys())[-1]
        latest_value = float(observations[latest_period])

        return {
            "country": country_code,
            "time": latest_period,
            "actual": latest_value,
            "expected": None  # 예상치는 별도 연동
        }
    except Exception as e:
        print(f"❌ {country_code} CPI 수집 실패: {e}")
        return None


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ JSON 로드 오류: {e}")
        return {}


def log_all_country_cpi():
    log = load_json(CPI_EVENT_LOG)
    for country in COUNTRY_CPI_CODES:
        cpi = fetch_latest_cpi_from_dbnomics(country)
        if not cpi:
            continue

        event_time = cpi['time']
        if event_time in log and country in log[event_time]:
            print(f"✅ 이미 기록된 {country} CPI ({event_time})")
            continue

        log.setdefault(event_time, {})[country] = {
            "actual": cpi["actual"],
            "logged_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"📌 {country} CPI 기록됨: {event_time} / {cpi['actual']}")

    save_json(CPI_EVENT_LOG, log)


def fetch_latest_cpis():
    """미국 CPI 최신값 리스트로 반환"""
    results = []
    for country in COUNTRY_CPI_CODES:
        cpi = fetch_latest_cpi_from_dbnomics(country)
        if cpi:
            results.append(cpi)
    return results


def auto_process_all_countries():
    """main.py에서 연결용 진입 함수"""
    return fetch_latest_cpis()


if __name__ == "__main__":
    log_all_country_cpi()




