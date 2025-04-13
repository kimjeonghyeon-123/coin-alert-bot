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

        record = {
            "timestamp": timestamp,
            "price": price,
            "volume": volume
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
    return history[-n:]
