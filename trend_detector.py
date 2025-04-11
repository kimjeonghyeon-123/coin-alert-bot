def get_current_trend(prices, short_window=5, long_window=20):
    """
    단기/장기 이동평균을 기반으로 현재 추세를 판단.

    :param prices: 가격 리스트
    :param short_window: 단기 이동평균 구간 (기본: 5)
    :param long_window: 장기 이동평균 구간 (기본: 20)
    :return: 'up', 'down', 'sideways'
    """
    if len(prices) < long_window:
        return "unknown"

    short_ma = sum(prices[-short_window:]) / short_window
    long_ma = sum(prices[-long_window:]) / long_window

    if short_ma > long_ma * 1.01:
        return "up"
    elif short_ma < long_ma * 0.99:
        return "down"
    else:
        return "sideways"
