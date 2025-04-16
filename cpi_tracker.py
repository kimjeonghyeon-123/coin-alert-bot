# 🔄 Multi-country CPI 자동 수집 + 업데이트

import json
import os
import requests
from datetime import datetime

# ✅ DBnomics 기반 CPI API (Eurostat - HICP 기준)
COUNTRY_CPI_CODES = {
    "USA": "USA.A.HICP.CPI.IX.CP00.N._Z",
    "KOR": "KOR.A.HICP.CPI.IX.CP00.N._Z",
    "JPN": "JPN.A.HICP.CPI.IX.CP00.N._Z",
    "DEU": "DEU.A.HICP.CPI.IX.CP00.N._Z",
    "FRA": "FRA.A.HICP.CPI.IX.CP00.N._Z",
    "GBR": "GBR.A.HICP.CPI.IX.CP00.N._Z"
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

        # 마지막 데이터
        latest_period = sorted(observations.keys())[-1]
        latest_value = float(observations[latest_period])

        return {
            "country": country_code,
            "time": latest_period,
            "actual": latest_value
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


if __name__ == "__main__":
    log_all_country_cpi()


