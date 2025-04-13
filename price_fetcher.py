import requests
import time

_cached_price = None
_cached_volume = None
_cached_time = 0
_cache_duration = 3  # seconds

GATEIO_TICKER_URL = "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT"

def get_current_price(pair="BTC_USDT"):
    global _cached_price, _cached_time

    now = time.time()
    if _cached_price is not None and (now - _cached_time) < _cache_duration:
        return _cached_price

    try:
        response = requests.get(GATEIO_TICKER_URL, timeout=5)
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

def get_price_and_volume(pair="BTC_USDT"):
    global _cached_price, _cached_volume, _cached_time

    now = time.time()
    if (_cached_price is not None and _cached_volume is not None
            and (now - _cached_time) < _cache_duration):
        return _cached_price, _cached_volume

    try:
        url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={pair}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            price = float(data[0].get('last', -1))
            volume = float(data[0].get('base_volume', -1))  # BTC 기준 거래량
        elif isinstance(data, dict):
            price = float(data.get('last', -1))
            volume = float(data.get('base_volume', -1))
        else:
            raise ValueError("API 응답에 가격 또는 거래량 정보 없음")

        _cached_price = price
        _cached_volume = volume
        _cached_time = now
        return price, volume

    except Exception as e:
        print(f"[❌ 가격/거래량 조회 실패] {e}")
        return (
            _cached_price if _cached_price is not None else -1,
            _cached_volume if _cached_volume is not None else -1,
        )
