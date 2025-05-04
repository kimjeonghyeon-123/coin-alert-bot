import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

# 두 점 사이 각도 계산
def calculate_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0:
        return 90
    radians = np.arctan2(dy, dx)
    degrees = np.degrees(radians)
    return abs(degrees)

# 각도에 따라 추세 세기 분류
def classify_angle(degree):
    if degree >= 60:
        return 'sharp'   # 강한 추세 (진입 고려)
    elif degree >= 30:
        return 'mild'    # 보통 추세
    else:
        return 'flat'    # 약한 추세 (관망)

# 고점/저점 기반 변곡점 탐지
def detect_inflection_points(prices, window=5):
    if isinstance(prices, dict):
        prices = sorted(prices.items())  # (timestamp, price) 리스트로 변환
    if len(prices) < window:
        return []

    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['price'] = df['price'].astype(float)
    df.set_index('timestamp', inplace=True)

    local_max = argrelextrema(df['price'].values, np.greater, order=window)[0]
    local_min = argrelextrema(df['price'].values, np.less, order=window)[0]

    inflection_indices = sorted(np.concatenate((local_max, local_min)))
    inflection_points = [(df.index[i], df['price'].iloc[i]) for i in inflection_indices]
    return inflection_points

# 추세 분석 + 변곡점 기반 전환 분석 + 진입 판단 요소 종합
def analyze_trend_angle_and_inflection(prices, angle_window=20, inflection_window=5):
    if isinstance(prices, dict):
        prices = sorted(prices.items())  # (timestamp, price) 리스트로 변환
    if len(prices) < angle_window:
        return {
            "angle": None,
            "angle_type": None,
            "inflection_points": [],
            "entry_signal": False,
            "trend_strength": "unknown",
            "direction": None
        }

    # 최근 추세선 분석 구간
    recent_data = prices[-angle_window:]
    timestamps, price_values = zip(*recent_data)
    x_vals = np.arange(len(price_values))
    y_vals = np.array(price_values)

    # 추세선 각도 계산
    x1, y1 = x_vals[0], y_vals[0]
    x2, y2 = x_vals[-1], y_vals[-1]
    angle = calculate_angle((x1, y1), (x2, y2))
    angle_type = classify_angle(angle)

    # 추세 방향 판단
    direction = "up" if y2 > y1 else "down"

    # 전체 구간에서 변곡점 분석
    inflection_points = detect_inflection_points(prices, window=inflection_window)

    # 최근 변곡점 이후 방향 확인
    recent_inflection_reversal = False
    if len(inflection_points) >= 2:
        _, p1 = inflection_points[-2]
        _, p2 = inflection_points[-1]
        if direction == "up" and p2 > p1:
            recent_inflection_reversal = True
        elif direction == "down" and p2 < p1:
            recent_inflection_reversal = True

    # 진입 시그널 판단 기준: 급한 각도 + 변곡점 직후 방향 일치
    entry_signal = angle_type == 'sharp' and recent_inflection_reversal

    # 매수/매도 강도 분류
    if angle_type == 'sharp' and direction == "up":
        trend_strength = "strong_buy"
    elif angle_type == 'sharp' and direction == "down":
        trend_strength = "strong_sell"
    elif angle_type == 'mild':
        trend_strength = "moderate"
    else:
        trend_strength = "weak"

    return {
        "angle": angle,
        "angle_type": angle_type,
        "inflection_points": inflection_points,
        "entry_signal": entry_signal,
        "trend_strength": trend_strength,
        "direction": direction
    }

