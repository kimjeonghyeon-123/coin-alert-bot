import os
import time
from keep_alive import keep_alive
from simulator import run_simulation
from price_logger import update_price
from entry_angle_detector import check_realtime_entry_signal
from config import MODE

# ✅ 추가된 import
from event_monitor import check_new_events
from notifier import send_event_alert

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
EVENT_CHECK_INTERVAL = 60  # ✅ 이벤트 체크 주기

# 타이머 초기화
t_last_price = time.time()
t_last_entry = time.time()
t_last_sim = time.time() - SIMULATION_INTERVAL + 5
t_last_event = time.time() - EVENT_CHECK_INTERVAL + 3  # ✅ 이벤트 감지용 타이머

keep_alive()
print("[시스템 시작] Bitcoin 실시간 모니터링 중...")

while True:
    now = time.time()

    if now - t_last_price >= PRICE_LOG_INTERVAL:
        update_price()
        t_last_price = now

    if now - t_last_entry >= ENTRY_SIGNAL_INTERVAL:
        check_realtime_entry_signal(is_pattern_allowed)  # trusted pattern 필터 넘김
        t_last_entry = now

    if now - t_last_sim >= SIMULATION_INTERVAL:
        run_simulation()
        t_last_sim = now

    # ✅ 이벤트 감지 실행
    if now - t_last_event >= EVENT_CHECK_INTERVAL:
        new_events = check_new_events()
        if new_events:
            for event in new_events:
                print(f"[이벤트 감지] {event['summary']} - 영향도: {event['impact']}")
                send_event_alert(event)
        t_last_event = now

    time.sleep(1)
