# chart_pattern_detector.py

def detect_chart_patterns(price_data):
    """
    더 정교한 패턴 분석이 필요한 경우 이곳에 구현.
    현재는 기본적인 패턴 감지를 위한 예시 반환.
    """
    # 예시: 가격이 최근 10개 중 상승한 개수가 많으면 'W-Pattern' 가정
    recent_prices = [float(x['close']) for x in price_data[-10:]]
    ups = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] > recent_prices[i-1])
    
    if ups >= 6:
        return "W-Pattern"
    elif ups <= 3:
        return "M-Pattern"
    return "None"
