def analyze_volume_behavior(volumes, prices, threshold=1.5):
    """
    거래량이 갑자기 증가한 시점을 분석해주는 함수.

    :param volumes: 거래량 리스트
    :param prices: 해당 시점의 가격 리스트
    :param threshold: 평균 대비 몇 배 이상일 때 강한 움직임으로 간주할지
    :return: 거래량 급증 시점들의 인덱스 리스트
    """
    if len(volumes) < 10:
        return []

    avg_volume = sum(volumes[:-5]) / len(volumes[:-5])
    spike_indices = []

    for i in range(-5, 0):
        if volumes[i] > avg_volume * threshold:
            spike_indices.append(len(volumes) + i)

    return spike_indices
