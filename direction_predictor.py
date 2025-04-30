def predict_both_directions(change_rate, volume_factor=1):
    """
    change_rate와 volume_factor를 기반으로 양방향 (long, short) 승률을 개별 계산
    """

    def calculate_conf(change_rate, volume_factor, direction):
        if direction == "long":
            if change_rate >= 1.0:
                base_conf = 0.75
            elif change_rate >= 0.5:
                base_conf = 0.65
            elif change_rate >= 0.2:
                base_conf = 0.55
            elif change_rate >= 0.0:
                base_conf = 0.45
            else:
                base_conf = 0.4
        else:  # short
            if change_rate <= -1.0:
                base_conf = 0.75
            elif change_rate <= -0.5:
                base_conf = 0.65
            elif change_rate <= -0.2:
                base_conf = 0.55
            elif change_rate <= 0.0:
                base_conf = 0.45
            else:
                base_conf = 0.4

        # 거래량 보정 (최대 ±0.05)
        if volume_factor > 1.5:
            base_conf += 0.05
        elif volume_factor > 1.2:
            base_conf += 0.03
        elif volume_factor < 0.5:
            base_conf -= 0.05
        elif volume_factor < 0.8:
            base_conf -= 0.03

        return round(max(0.1, min(0.99, base_conf)), 3)

    return {
        "long": {"confidence": calculate_conf(change_rate, volume_factor, "long")},
        "short": {"confidence": calculate_conf(change_rate, volume_factor, "short")},
    }
