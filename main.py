# main.py (Render 배포용 실전 버전)
import os
import time
from keep_alive import keep_alive
from simulator import run_simulation
from price_logger import update_price
from entry_angle_detector import check_realtime_entry_signal

# 주기 설정 (초 단위)
PRICE_LOG_INTERVAL = 60
ENTRY_SIGNAL_INTERVAL = 30
SIMULATION_INTERVAL = 10800  # 3시간

# 타이머 초기화
t_last_price = time.time()
t_last_entry = time.time()
t_last_sim = time.time() - SIMULATION_INTERVAL + 5  # 부팅 직후 1회 실행

keep_alive()  # Render 환경용 웹서버 실행
print("[시스템 시작] Bitcoin 실시간 모니터링 중...")

while True:
    now = time.time()

    # 실시간 가격 업데이트
    if now - t_last_price >= PRICE_LOG_INTERVAL:
        update_price()
        t_last_price = now

    # 진입각 체크
    if now - t_last_entry >= ENTRY_SIGNAL_INTERVAL:
        check_realtime_entry_signal()
        t_last_entry = now

    # 시뮬레이션 실행
    if now - t_last_sim >= SIMULATION_INTERVAL:
        run_simulation()
        t_last_sim = now

    time.sleep(1)
