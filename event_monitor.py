# event_monitor.py
import requests
import time
from datetime import datetime
from notifier import send_telegram_message

# 더미 API (실제 URL로 교체 필요)
NEWS_API_URL = "https://example-news-api.com/bitcoin/events"
ECONOMIC_DATA_URL = "https://example-economy-api.com/releases"
ORDER_FLOW_API = "https://example-whale-tracker.com/flows"

# 최근 감지된 이벤트들 저장
recent_events = []

def fetch_recent_news():
    try:
        response = requests.get(NEWS_API_URL)
        if response.status_code == 200:
            return response.json()  # [{"title": "...", "impact": "high", "timestamp": ...}]
    except Exception as e:
        print(f"[뉴스 수집 오류] {e}")
    return []

def fetch_economic_indicators():
    try:
        response = requests.get(ECONOMIC_DATA_URL)
        if response.status_code == 200:
            return response.json()  # [{"indicator": "CPI", "value": 3.2, "expected": 3.1}]
    except Exception as e:
        print(f"[경제지표 수집 오류] {e}")
    return []

def fetch_order_flow():
    try:
        response = requests.get(ORDER_FLOW_API)
        if response.status_code == 200:
            return response.json()  # [{"type": "sell", "amount": 1200, "price": 69200}]
    except Exception as e:
        print(f"[고래흐름 수집 오류] {e}")
    return []

def analyze_event_impact(event):
    # 간단한 영향 점수 계산
    if event.get("impact") == "high":
        return 0.8
    elif event.get("impact") == "medium":
        return 0.5
    return 0.2

def is_duplicate_event(summary):
    now = time.time()
    for e in recent_events:
        if e["summary"] == summary and now - e["timestamp"] < 300:
            return True
    return False

def check_new_events():
    global recent_events

    news = fetch_recent_news()
    indicators = fetch_economic_indicators()
    order_flows = fetch_order_flow()

    high_impact_events = []

    for item in news:
        impact_score = analyze_event_impact(item)
        if impact_score >= 0.7 and not is_duplicate_event(item["title"]):
            high_impact_events.append(("뉴스", item["title"], impact_score))

    for econ in indicators:
        surprise = abs(econ["value"] - econ["expected"]) / econ["expected"]
        if surprise > 0.05:
            summary = f"{econ['indicator']} 발표 - 예상치 대비 변화율 {round(surprise*100, 1)}%"
            if not is_duplicate_event(summary):
                high_impact_events.append(("경제지표", summary, round(surprise, 2)))

    for flow in order_flows:
        if flow["amount"] >= 1000:
            summary = f"{flow['type']} {flow['amount']} BTC @ {flow['price']}"
            if not is_duplicate_event(summary):
                high_impact_events.append(("고래매매", summary, 0.9))

    for kind, detail, score in high_impact_events:
        event_obj = {
            "summary": f"{kind}: {detail}",
            "impact": "high" if score >= 0.7 else "medium",
            "timestamp": time.time()
        }
        recent_events.append(event_obj)

        msg = f"🚨 *{kind} 이벤트 감지됨*\n내용: `{detail}`\n영향 추정 점수: {score}"
        send_telegram_message(msg)

    return high_impact_events

# 최근 10분 이내 이벤트 조회 (시뮬레이션 등에서 사용)
def get_recent_events():
    cutoff = time.time() - 600
    return [e for e in recent_events if e["timestamp"] >= cutoff]

if __name__ == "__main__":
    check_new_events()
