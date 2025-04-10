# price_fetcher.py
import requests

def get_current_price():
    try:
        response = requests.get("https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT")
        data = response.json()[0]
        return float(data['last'])
    except Exception as e:
        print(f"[가격 조회 오류] {e}")
        return None
