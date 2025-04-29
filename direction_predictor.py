def predict_direction(change_rate, volume_factor=1):
    """
    변화율 + 거래량 팩터 기반으로 진입 방향(long/short)과 신뢰도 계산
    volume_factor는 거래량 분석으로 도출된 지표. 1보다 크면 평소보다 많음.
    """

    # 1단계: 변화율 기반 초기 판단
    if change_rate >= 1.0:
        direction, base_conf = "long", 0.75
    elif change_rate <= -1.0:
        direction, base_conf = "short", 0.75
    elif change_rate >= 0.5:
        direction, base_conf = "long", 0.65
    elif change_rate <= -0.5:
        direction, base_conf = "short", 0.65
    elif change_rate >= 0.2:
        direction, base_conf = "long", 0.55
    elif change_rate <= -0.2:
        direction, base_conf = "short", 0.55
    else:
        # 변화율이 너무 낮으면 가장 가까운 방향으로 설정하되 낮은 신뢰도
        direction = "long" if change_rate >= 0 else "short"
        base_conf = 0.45

    # 2단계: 거래량 보정
    # 거래량이 평균보다 많으면 신뢰도 증가, 적으면 감소 (최대 ±0.05)
    if volume_factor > 1.5:
        base_conf += 0.05
    elif volume_factor > 1.2:
        base_conf += 0.03
    elif volume_factor < 0.5:
        base_conf -= 0.05
    elif volume_factor < 0.8:
        base_conf -= 0.03

    # 3단계: 경계 조건 보정
    base_conf = max(0.1, min(0.99, base_conf))

    return direction, round(base_conf, 3)

