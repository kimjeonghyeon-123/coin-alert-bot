import requests
import time

_cached_price = None
_cached_time = 0
_cache_duration = 3  # seconds

GATEIO_TICKER_URL = "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT"

def get_current_price(pair="BTC_USDT"):
    global _cached_price, _cached_time

    now = time.time()
    if _cached_price is not None and (now - _cached_time) < _cache_duration:
        return _cached_price

    try:
        url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={pair}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0 and 'last' in data[0]:
            price = float(data[0]['last'])
        elif isinstance(data, dict) and 'last' in data:
            price = float(data['last'])
        else:
            raise ValueError("API 응답에 'last' 가격 정보 없음")

        _cached_price = price
        _cached_time = now
        return price
    except Exception as e:
        print(f"[❌ 가격 조회 실패] {e}")
        return _cached_price if _cached_price is not None else -1

