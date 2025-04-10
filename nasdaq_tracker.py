# nasdaq_tracker.py

import requests
import datetime

def fetch_nasdaq_history():
    """
    과거 나스닥 지수 데이터 수집 (예: Yahoo Finance, Alpha Vantage)
    """
    nasdaq_data = []  # timestamp, 종가, 변동률 등
    return nasdaq_data

def get_nasdaq_current():
    """
    현재 나스닥 실시간 지수 가져오기 (예: 매일 장 마감 시)
    """
    return {
        "timestamp": str(datetime.datetime.now()),
        "price": 13220.0
    }
