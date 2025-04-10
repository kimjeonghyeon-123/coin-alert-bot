import numpy as np
import pandas as pd
from scipy.signal import argrelextrema


def calculate_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0:
        return 90
    radians = np.arctan2(dy, dx)
    degrees = np.degrees(radians)
    return abs(degrees)


def classify_angle(degree):
    if degree >= 60:
        return 'sharp'
    elif degree >= 30:
        return 'mild'
    else:
        return 'flat'


def detect_inflection_points(prices, window=5):
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['price'] = df['price'].astype(float)
    df.set_index('timestamp', inplace=True)

    local_max = argrelextrema(df['price'].values, np.greater, order=window)[0]
    local_min = argrelextrema(df['price'].values, np.less, order=window)[0]

    inflection_indices = sorted(np.concatenate((local_max, local_min)))
    inflection_points = [(df.index[i], df['price'].iloc[i]) for i in inflection_indices]
    return inflection_points


def analyze_trend_angle_and_inflection(prices, angle_window=20):
    if len(prices) < angle_window:
        return None, [], None

    # 가격 데이터 정제
    recent_data = prices[-angle_window:]
    timestamps, price_values = zip(*recent_data)
    x_vals = np.arange(len(price_values))
    y_vals = np.array(price_values)

    # 추세선 기울기 계산
    x1, y1 = x_vals[0], y_vals[0]
    x2, y2 = x_vals[-1], y_vals[-1]
    angle = calculate_angle((x1, y1), (x2, y2))
    angle_type = classify_angle(angle)

    # 변곡점 탐지
    inflection_points = detect_inflection_points(prices)

    return angle, inflection_points, angle_type
