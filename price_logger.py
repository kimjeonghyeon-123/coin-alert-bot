# price_logger.py
import os
import requests
import time
import json

price_log_file = "price_history.json"

# 가격 기록
def update_price():
    try:
        response = requests.get("https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT")
        data = response.json()[0]
        price = float(data['last'])
        timestamp = int(time.time())

        record = {"timestamp": timestamp, "price": price}

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

        print(f"[가격 기록] {timestamp} - {price}")

    except Exception as e:
        print(f"[가격 업데이트 오류] {e}")

# 최근 가격 기록 가져오기
def get_recent_prices(n=30):
    if not os.path.exists(price_log_file):
        return []
    with open(price_log_file, "r") as f:
        history = json.load(f)
    return history[-n:]
