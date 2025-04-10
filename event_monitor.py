# event_monitor.py
import requests
import json
from datetime import datetime
from notifier import send_telegram_message

# 임시 예시 데이터 소스들 (나중에 실제 API나 데이터 소스로 대체 가능)
NEWS_API_URL = "https://example-news-api.com/bitcoin/events"
ECONOMIC_DATA_URL = "https://example-economy-api.com/releases"
ORDER_FLOW_API = "https://example-whale-tracker.com/flows"


def fetch_recent_news():
    try:
        response = requests.get(NEWS_API_URL)
        if response.status_code == 200:
            return response.json()  # [{"title": "SEC announces...", "impact": "high", "timestamp": ...}, ...]
    except Exception as e:
        print(f"[뉴스 수집 오류] {e}")
    return []


def fetch_economic_indicators():
    try:
        response = requests.get(ECONOMIC_DATA_URL)
        if response.status_code == 200:
            return response.json()  # [{"indicator": "CPI", "value": 3.2, "expected": 3.1, ...}]
    except Exception as e:
        print(f"[경제지표 수집 오류] {e}")
    return []


def fetch_order_flow():
    try:
        response = requests.get(ORDER_FLOW_API)
        if response.status_code == 200:
            return response.json()  # [{"type": "sell", "amount": 1200, "price": 69200}, ...]
    except Exception as e:
        print(f"[고래흐름 수집 오류] {e}")
    return []


def analyze_event_impact(event):
    # 여기에 과거 학습된 유사 이벤트와의 비교 및 영향 추정 로직 삽입 가능
    if event.get("impact") == "high":
        return 0.8
    elif event.get("impact") == "medium":
        return 0.5
    return 0.2


def check_new_events():
    news = fetch_recent_news()
    indicators = fetch_economic_indicators()
    order_flows = fetch_order_flow()

    high_impact_events = []

    for item in news:
        impact = analyze_event_impact(item)
        if impact >= 0.7:
            high_impact_events.append(("뉴스", item["title"], impact))

    for econ in indicators:
        surprise = abs(econ["value"] - econ["expected"]) / econ["expected"]
        if surprise > 0.05:
            high_impact_events.append(("경제지표", econ["indicator"], round(surprise, 2)))

    for flow in order_flows:
        if flow["amount"] >= 1000:
            high_impact_events.append(("고래매매", f"{flow['type']} {flow['amount']} BTC @ {flow['price']}", 0.9))

    for kind, detail, score in high_impact_events:
        msg = f"🚨 *{kind} 이벤트 감지됨*
내용: `{detail}`
영향 추정 점수: {score}"
        send_telegram_message(msg)

    return high_impact_events


if __name__ == "__main__":
    check_new_events()
