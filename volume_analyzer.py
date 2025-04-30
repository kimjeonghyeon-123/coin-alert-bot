def analyze_volume_behavior(volumes, prices, threshold=1.5):
    """
    거래량이 갑자기 증가한 정도를 분석해주는 함수.

    :param volumes: 거래량 리스트
    :param prices: 해당 시점의 가격 리스트
    :param threshold: 평균 대비 몇 배 이상일 때 강한 움직임으로 간주할지
    :return: 거래량 급증 정도를 나타내는 float 값 (1 이상일 경우 거래량 급증)
    """
    if not volumes or len(volumes) < 10:
        return 1  # 거래량 데이터가 부족하면 기본값으로 1을 반환

    if len(volumes) <= 5:
        return 1  # 분모가 0이 되지 않도록 안전장치

    recent_volumes = volumes[:-5]
    if not recent_volumes:
        return 1

    avg_volume = sum(recent_volumes) / len(recent_volumes)
    volume_factor = 1

    for i in range(-5, 0):
        if i >= -len(volumes):  # 인덱스 범위 체크
            if volumes[i] > avg_volume * threshold:
                volume_factor += 0.1

    return volume_factor


