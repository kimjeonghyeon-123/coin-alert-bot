import json

def load_learning_stats():
    with open("learning_stats.json", "r") as f:
        return json.load(f)

def adjust_confidence(base_confidence, detected_patterns=[], direction=None, trend=None, event_key=None):
    stats = load_learning_stats()
    confidence = base_confidence

    # 📊 패턴별 정확도 조정
    for pattern in detected_patterns:
        if pattern in stats["patterns"]:
            p_stats = stats["patterns"][pattern]
            total = p_stats["success"] + p_stats["fail"]
            if total >= 5:  # 최소 학습 필요치
                success_rate = p_stats["success"] / total
                confidence += (success_rate - 0.5) * 0.4  # ±20% 조정

    # 📈 추세 정확도 조정
    if trend and trend in stats["trend"]:
        t_stats = stats["trend"][trend]
        total = t_stats["success"] + t_stats["fail"]
        if total >= 3:
            success_rate = t_stats["success"] / total
            confidence += (success_rate - 0.5) * 0.3

    # 🔄 방향 정확도 조정
    if direction and direction in stats["direction"]:
        d_stats = stats["direction"][direction]
        total = d_stats["success"] + d_stats["fail"]
        if total >= 3:
            success_rate = d_stats["success"] / total
            confidence += (success_rate - 0.5) * 0.3

    # 📅 이벤트 지속 시간 조정도 추후 확장 가능
    confidence = max(0, min(1, confidence))  # 0~1 사이로 제한
    return round(confidence, 3)
