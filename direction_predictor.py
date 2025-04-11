def predict_direction(change_rate):
    """
    5분간 변화율 기반으로 long/short 판단과 기본 확률 계산
    """
    if change_rate > 0.5:
        return "long", 0.65
    elif change_rate < -0.5:
        return "short", 0.65
    elif change_rate > 0.2:
        return "long", 0.55
    elif change_rate < -0.2:
        return "short", 0.55
    else:
        return "neutral", 0.4
