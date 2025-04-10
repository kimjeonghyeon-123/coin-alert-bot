# price_fetcher.py
import requests
import time

_cached_price = None
_cached_time = 0
_cache_duration = 3  # seconds

def get_current_price():
    global _cached_price, _cached_time

    now = time.time()
    if _cached_price is not None and (now - _cached_time) < _cache_duration:
        return _cached_price

    try:
        response = requests.get("https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT")
        data = response.json()[0]
        price = float(data['last'])

        _cached_price = price
        _cached_time = now
        return price
    except Exception as e:
        print(f"[가격 조회 오류] {e}")
        return _cached_price  # 최근 캐시라도 리턴 (없으면 None)
