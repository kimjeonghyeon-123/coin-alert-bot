# utils.py

def moving_average(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period
