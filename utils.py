import json
import os

def moving_average(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

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

