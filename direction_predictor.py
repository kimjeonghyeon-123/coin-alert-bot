def predict_direction(change_rate, volume_factor=1):
    """
    5분간 변화율 + 거래량 팩터 기반으로 long/short 판단과 기본 확률 계산
    volume_factor는 거래량 분석을 통해 도출된 지표로, 1보다 크면 평소보다 거래량 많음
    """

    # 기본 방향 및 신뢰도 판단
    if change_rate > 0.5:
        direction, base_conf = "long", 0.65
    elif change_rate < -0.5:
        direction, base_conf = "short", 0.65
    elif change_rate > 0.2:
        direction, base_conf = "long", 0.55
    elif change_rate < -0.2:
        direction, base_conf = "short", 0.55
    else:
        direction, base_conf = "neutral", 0.4

    # 거래량에 따라 신뢰도 보정 (±0.05 한도 내)
    if volume_factor > 1.2:
        base_conf += 0.03
    elif volume_factor < 0.8:
        base_conf -= 0.03

    # 신뢰도는 0~1 사이로 제한
    base_conf = max(0, min(1, base_conf))

    return direction, base_conf
