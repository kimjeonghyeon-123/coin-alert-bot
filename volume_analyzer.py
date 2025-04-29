def analyze_volume_behavior(volumes, prices, threshold=1.5):
    """
    거래량이 갑자기 증가한 정도를 분석해주는 함수.

    :param volumes: 거래량 리스트
    :param prices: 해당 시점의 가격 리스트
    :param threshold: 평균 대비 몇 배 이상일 때 강한 움직임으로 간주할지
    :return: 거래량 급증 정도를 나타내는 float 값 (1 이상일 경우 거래량 급증)
    """
    if len(volumes) < 10:
        return 1  # 거래량 데이터가 부족하면 기본값으로 1을 반환

    avg_volume = sum(volumes[:-5]) / len(volumes[:-5])  # 마지막 5개를 제외한 평균 거래량
    volume_factor = 1  # 기본 거래량 팩터는 1로 설정

    for i in range(-5, 0):
        if volumes[i] > avg_volume * threshold:
            volume_factor += 0.1  # 거래량 급증시, 거래량 팩터를 증가시킴

    return volume_factor

