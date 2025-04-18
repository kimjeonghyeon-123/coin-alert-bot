import os
import time
from keep_alive import keep_alive
from simulator import run_simulation
from price_logger import update_price
from entry_angle_detector import check_realtime_entry_signal, detect_chart_patterns
from config import MODE

# ✅ 이벤트 감지 관련 import
from event_monitor import check_new_events, get_recent_events
from notifier import send_event_alert

# ✅ 다국가 CPI 자동 처리
from multi_country_cpi_fetcher import auto_process_all_countries  # 새로 추가된 import

# trusted_patterns 적용
if MODE == "real":
    from trusted_patterns import TRUSTED_PATTERNS
else:
    TRUSTED_PATTERNS = None

def is_pattern_allowed(pattern_name):
    if TRUSTED_PATTERNS is None:
        return True
    return pattern_name in TRUSTED_PATTERNS

# 주기 설정 (초 단위)
PRICE_LOG_INTERVAL = 60
ENTRY_SIGNAL_INTERVAL = 30
SIMULATION_INTERVAL = 10800  # 3시간
EVENT_CHECK_INTERVAL = 60
CPI_PROCESS_INTERVAL = 3600  # 1시간마다 다국가 CPI 체크

# 타이머 초기화
t_last_price = time.time()
t_last_entry = time.time()
t_last_sim = time.time() - SIMULATION_INTERVAL + 5
t_last_event = time.time() - EVENT_CHECK_INTERVAL + 3
t_last_cpi = time.time() - CPI_PROCESS_INTERVAL + 10  # 바로 시작

keep_alive()
print("[시스템 시작] Bitcoin 실시간 모니터링 중...")

while True:
    now = time.time()

    # 가격 기록
    if now - t_last_price >= PRICE_LOG_INTERVAL:
        update_price()
        t_last_price = now

    # 실시간 진입 각도 체크
    if now - t_last_entry >= ENTRY_SIGNAL_INTERVAL:
        recent_events = get_recent_events()

        # 패턴 감지 및 진입 신호 판단
        patterns = detect_chart_patterns(recent_events)
        check_realtime_entry_signal(is_pattern_allowed)

        t_last_entry = now

    # 시뮬레이션 실행
    if now - t_last_sim >= SIMULATION_INTERVAL:
        recent_events = get_recent_events()
        run_simulation(recent_events=recent_events)
        t_last_sim = now

    # 이벤트 감지
    if now - t_last_event >= EVENT_CHECK_INTERVAL:
        new_events = check_new_events()
        if new_events:
            for event in new_events:
                print(f"[이벤트 감지] {event['summary']} - 영향도: {event['impact']}")
                send_event_alert(event)
        t_last_event = now

    # ✅ 다국가 CPI 자동 처리
    if now - t_last_cpi >= CPI_PROCESS_INTERVAL:
        auto_process_all_countries()
        t_last_cpi = now
