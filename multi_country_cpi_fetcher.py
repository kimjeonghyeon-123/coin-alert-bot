import json
import os
import requests
from datetime import datetime

# ✅ 미국 CPI 코드 (FRED 코드 기준)
COUNTRY_CPI_CODES = {
    "USA": "CPIAUCNS"  # 미국 전체 도시 소비자물가지수 (Consumer Price Index for All Urban Consumers)
}

# ✅ FRED API 키
FRED_API_KEY = "4c660d85c6caa3480c4dd60c1e2fa823"

CPI_EVENT_LOG = "cpi_event_log.json"


def fetch_latest_cpi_from_dbnomics(country_code):
    """
    함수 이름은 유지하되, 내부는 FRED API 기반으로 동작하게 수정.
    """
    series_code = COUNTRY_CPI_CODES[country_code]
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_code,
        "api_key": FRED_API_KEY,
        "file_type": "json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        observations = data.get("observations", [])
        if not observations:
            raise ValueError("관측값 없음")

        latest_entry = observations[-1]
        latest_period = latest_entry["date"]
        latest_value = float(latest_entry["value"])

        expected_value = None  # 추후 예측치 연동 예정

        return {
            "country": country_code,
            "time": latest_period,
            "actual": latest_value,
            "expected": expected_value
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
            "expected": cpi["expected"],
            "logged_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"📌 {country} CPI 기록됨: {event_time} / {cpi['actual']}")

    save_json(CPI_EVENT_LOG, log)


def fetch_latest_cpis():
    results = []
    for country in COUNTRY_CPI_CODES:
        cpi = fetch_latest_cpi_from_dbnomics(country)
        if cpi:
            results.append(cpi)
    return results


def auto_process_all_countries():
    return fetch_latest_cpis()


if __name__ == "__main__":
    log_all_country_cpi()






