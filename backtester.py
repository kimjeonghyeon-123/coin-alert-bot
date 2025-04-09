import csv
import time
from simulator import simulate_entry
from pattern_trainer import update_pattern_stats

def load_historical_data(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def run_backtest(filepath):
    data = load_historical_data(filepath)
    results = []

    for i in range(100, len(data) - 12):  # 최소 100봉 이후부터 예측, 12봉 이후 결과 판단
        current_slice = data[i - 100:i]
        current_price = float(data[i]['close'])
        timestamp = data[i]['timestamp']

        prediction = simulate_entry(current_slice, current_price, simulate_mode=True)
        actual_result = simulate_future_outcome(data[i:i+12], prediction)

        update_pattern_stats(prediction, actual_result)
        results.append((timestamp, prediction["direction"], actual_result))
        
        time.sleep(0.005)  # 과부하 방지

    return results

def simulate_future_outcome(future_data, prediction):
    if not future_data:
        return "fail"

    entry_price = prediction["entry_price"]
    direction = prediction["direction"]
    sl = prediction["stop_loss"]
    tp = prediction["take_profit"]

    for candle in future_data:
        high = float(candle['high'])
        low = float(candle['low'])

        if direction == "long":
            if low <= sl:
                return "fail"
            if high >= tp:
                return "success"
        elif direction == "short":
            if high >= sl:
                return "fail"
            if low <= tp:
                return "success"

    return "fail"
