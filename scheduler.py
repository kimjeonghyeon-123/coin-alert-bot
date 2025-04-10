import schedule
import time
from price_logger import log_price
from cpi_tracker import auto_process_cpi_event
from nasdaq_tracker import check_nasdaq_event

# ✅ 1분마다 BTC 가격 기록
schedule.every(1).minutes.do(log_price)

# ✅ 30분마다 최신 CPI 확인 및 처리
schedule.every(30).minutes.do(auto_process_cpi_event)

# ✅ 1분마다 나스닥 변동 감지
schedule.every(1).minutes.do(check_nasdaq_event)

# 추후: S&P500 등 추가 가능

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()

