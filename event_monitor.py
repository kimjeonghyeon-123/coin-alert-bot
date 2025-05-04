import requests
import time
from datetime import datetime
from notifier import send_telegram_message

NEWS_API_URL = "https://cryptopanic.com/api/v1/posts/?auth_token=YOUR_TOKEN&currencies=BTC"
ECONOMIC_DATA_URL = "https://www.alphavantage.co/query?function=CPI&apikey=YOUR_API_KEY"
ORDER_FLOW_API = "https://api.whale-alert.io/v1/transactions?api_key=YOUR_API_KEY&min_value=500000"

recent_events = []

def fetch_recent_news():
    try:
        response = requests.get(NEWS_API_URL)
        if response.status_code == 200:
            posts = response.json().get("results", [])
            return [{"title": p.get("title", ""), "impact": None, "timestamp": time.time()} for p in posts]
    except Exception as e:
        print(f"[뉴스 수집 오류] {e}")
    return []

def fetch_economic_indicators():
    try:
        response = requests.get(ECONOMIC_DATA_URL)
        if response.status_code == 200:
            # 실제로는 JSON 파싱 필요하지만 예시는 고정값
            return [{"indicator": "CPI", "value": 3.2, "expected": 3.1, "timestamp": time.time()}]
    except Exception as e:
        print(f"[경제지표 수집 오류] {e}")
    return []

def fetch_order_flow():
    try:
        response = requests.get(ORDER_FLOW_API)
        if response.status_code == 200:
            data = response.json().get("transactions", [])
            return [
                {
                    "type": tx.get("transaction_type", "unknown"),
                    "amount": tx.get("amount", 0),
                    "price": tx.get("amount_usd", 0),
                    "timestamp": tx.get("timestamp", time.time())
                }
                for tx in data
            ]
    except Exception as e:
        print(f"[고래흐름 수집 오류] {e}")
    return []

def analyze_event_impact(event):
    title = event.get("title", "").lower()

    hot_keywords = ["hot", "hawkish", "fear", "regulation", "crackdown", "rate hike", "inflation"]
    medium_keywords = ["inline", "moderate", "neutral"]
    low_keywords = ["cool", "dovish", "calm", "relief"]

    for kw in hot_keywords:
        if kw in title:
            return 0.9
    for kw in medium_keywords:
        if kw in title:
            return 0.6
    for kw in low_keywords:
        if kw in title:
            return 0.3

    return 0.2

def is_duplicate_event(summary):
    now = time.time()
    for e in recent_events:
        if e.get("summary") == summary and now - e.get("timestamp", 0) < 300:
            return True
    return False

def trim_recent_events(limit=100):
    global recent_events
    recent_events = recent_events[-limit:]

def check_new_events():
    global recent_events

    news = fetch_recent_news()
    indicators = fetch_economic_indicators()
    order_flows = fetch_order_flow()

    high_impact_events = []

    for item in news:
        title = item.get("title", "")
        impact_score = analyze_event_impact(item)
        if impact_score >= 0.7 and not is_duplicate_event(title):
            high_impact_events.append(("뉴스", title, impact_score))

    for econ in indicators:
        actual = econ.get("value")
        expected = econ.get("expected")
        if actual is not None and expected not in (None, 0):
            try:
                surprise = abs(actual - expected) / expected
                if surprise > 0.05:
                    summary = f"{econ.get('indicator', '지표')} 발표 - 예상치 대비 변화율 {round(surprise*100, 1)}%"
                    if not is_duplicate_event(summary):
                        score = min(0.8, 0.4 + surprise)
                        high_impact_events.append(("경제지표", summary, round(score, 2)))
            except Exception as e:
                print(f"[경제지표 분석 오류] {e}")

    for flow in order_flows:
        amount = flow.get("amount", 0)
        price = flow.get("price", 0)
        ftype = flow.get("type", "unknown")
        if amount >= 1000:
            summary = f"{ftype} {round(amount, 2)} BTC @ ${round(price, 0):,.0f}"
            if not is_duplicate_event(summary):
                high_impact_events.append(("고래매매", summary, 0.9))

    for kind, detail, score in high_impact_events:
        event_obj = {
            "summary": f"{kind}: {detail}",
            "impact": "high" if score >= 0.7 else "medium" if score >= 0.4 else "low",
            "timestamp": time.time()
        }
        recent_events.append(event_obj)
        trim_recent_events()

        try:
            # 텔레그램 메시지 이스케이프 처리
            safe_detail = detail.replace("`", "'").replace("*", "")
            msg = f"🚨 *{kind} 이벤트 감지됨*\n내용: `{safe_detail}`\n영향 추정 점수: {score}"
            send_telegram_message(msg)
        except Exception as e:
            print(f"[텔레그램 전송 오류] {e}")

    return high_impact_events

def get_recent_events():
    cutoff = time.time() - 600
    return [e for e in recent_events if e.get("timestamp", 0) >= cutoff]

if __name__ == "__main__":
    check_new_events()

