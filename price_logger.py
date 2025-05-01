import os
import time
import json
from price_fetcher import get_price_and_volume  # 수정된 함수 사용

price_log_file = "price_history.json"

# 가격 및 거래량 기록
def update_price():
    try:
        price, volume = get_price_and_volume()
        timestamp = int(time.time())

        # 🛡 price가 dict인 경우 평탄화 (예: {'usd': 63700.0} -> 63700.0)
        if isinstance(price, dict):
            price = price.get("usd") or price.get("close") or list(price.values())[0]
        
        if not isinstance(price, (int, float)):
            raise ValueError(f"[❌ 오류] price 값이 숫자가 아님: {price}")

        if volume is None:
            print("[⚠️ 경고] 거래량이 None으로 반환되었습니다. 0으로 대체합니다.")
            volume = 0

        record = {
            "timestamp": timestamp,
            "price": float(price),
            "volume": float(volume)
        }

        if os.path.exists(price_log_file):
            with open(price_log_file, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(record)

        # 최근 500개만 유지
        history = history[-500:]

        with open(price_log_file, "w") as f:
            json.dump(history, f)

        print(f"[📈 가격 기록] {timestamp} - {price} / 거래량: {volume}")

    except Exception as e:
        print(f"[❌ 가격 업데이트 오류] {e}")

# 최근 가격 기록 가져오기
def get_recent_prices(n=30):
    if not os.path.exists(price_log_file):
        return []
    with open(price_log_file, "r") as f:
        history = json.load(f)

    # 🛡 데이터 일관성 검사 및 정제
    cleaned = []
    for item in history[-n:]:
        try:
            price = item["price"]
            if isinstance(price, dict):
                price = price.get("usd") or price.get("close") or list(price.values())[0]
            cleaned.append({
                "timestamp": int(item["timestamp"]),
                "price": float(price),
                "volume": float(item.get("volume", 0))
            })
        except Exception as e:
            print(f"[⚠️ 스킵됨] 잘못된 데이터: {item}, 오류: {e}")
    return cleaned


