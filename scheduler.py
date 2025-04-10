# scheduler.py

import time
from nasdaq_tracker import auto_monitor_nasdaq

def run_nasdaq_monitor_loop():
    while True:
        try:
            auto_monitor_nasdaq()
        except Exception as e:
            print("❌ 자동 모니터링 오류:", e)
        time.sleep(60)  # 1분마다 실행
