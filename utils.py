import json
import os

def moving_average(data, period):
    """
    이동 평균 계산 (list 또는 dict 모두 지원)
    - list: 단순 최근 N개 평균
    - dict: 시간순 정렬 후 최근 N개 평균
    """
    if isinstance(data, dict):
        sorted_values = [v for k, v in sorted(data.items())]
    else:
        sorted_values = data

    if len(sorted_values) < period:
        return None

    return sum(sorted_values[-period:]) / period

def load_learning_stats(file_path='learning_stats.json'):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

def load_weights(file_path='weights.json'):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)


