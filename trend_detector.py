def get_current_trend(prices, volumes=None, short_window=5, long_window=20):
    """
    단기/장기 이동평균을 기반으로 현재 추세를 판단.
    거래량이 낮으면 확신도 줄이고 'sideways' 경향 높임.

    :param prices: 가격 리스트
    :param volumes: 거래량 리스트 (선택)
    :param short_window: 단기 이동평균 구간 (기본: 5)
    :param long_window: 장기 이동평균 구간 (기본: 20)
    :return: 'up', 'down', 'sideways', 'unknown'
    """
    if len(prices) < long_window:
        return "unknown"

    short_ma = sum(prices[-short_window:]) / short_window
    long_ma = sum(prices[-long_window:]) / long_window

    price_trend = "sideways"
    if short_ma > long_ma * 1.01:
        price_trend = "up"
    elif short_ma < long_ma * 0.99:
        price_trend = "down"

    # 🔸 거래량 기반 보정
    if volumes and len(volumes) >= long_window:
        recent_volumes = volumes[-long_window:]
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        latest_volume = volumes[-1]

        if latest_volume < avg_volume * 0.7:
            # 거래량이 너무 낮으면 추세 확신 낮음
            return "sideways"

    return price_trend

