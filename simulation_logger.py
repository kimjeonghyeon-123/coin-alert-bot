import json
import os
import uuid
import time
from datetime import datetime
from price_logger import get_current_price
from notifier import send_telegram_message

LOG_FILE = "simulation_log.json"


def log_simulation_result(sim_result):
    """
    sim_result: dict with keys:
      - timestamp (unix)
      - direction: 'long' or 'short'
      - entry: 진입가
      - take_profit
      - stop_loss
      - expected_winrate
      - pattern
      - moving_averages: {ma5, ma20, ma60}
      - volume_profile: optional
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcfromtimestamp(sim_result["timestamp"]).isoformat(),
        "unix_timestamp": sim_result["timestamp"],
        "direction": sim_result["direction"],
        "entry_price": sim_result["entry"],
        "take_profit": sim_result["take_profit"],
        "stop_loss": sim_result["stop_loss"],
        "expected_winrate": sim_result["expected_winrate"],
        "pattern": sim_result.get("pattern"),
        "moving_averages": sim_result.get("moving_averages"),
        "volume_profile": sim_result.get("volume_profile"),
        "evaluated": False,
        "result": None
    }

    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(log_entry)
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Logging simulation result failed: {e}")


def check_simulation_results():
    if not os.path.exists(LOG_FILE):
        return

    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load log file: {e}")
        return

    current_price = get_current_price()
    now = int(time.time())
    updated = False

    for log in logs:
        if log.get("evaluated", False):
            continue

        elapsed = now - log["unix_timestamp"]
        if elapsed < 1800:  # 평가까지 30분 대기
            continue

        direction = log["direction"]
        tp = log["take_profit"]
        sl = log["stop_loss"]

        result = None
        if direction == "long":
            if current_price >= tp:
                result = "success"
            elif current_price <= sl:
                result = "fail"
        else:
            if current_price <= tp:
                result = "success"
            elif current_price >= sl:
                result = "fail"

        if result:
            log["evaluated"] = True
            log["result"] = result
            updated = True

            msg = f"""📘 *시뮬레이션 평가 결과*
*방향:* {direction.upper()}
*진입가:* {log['entry_price']:.2f}
*TP / SL:* {tp:.2f} / {sl:.2f}
*현재가:* {current_price:.2f}
*결과:* {'✅ 익절 성공' if result == 'success' else '❌ 손절 실패'}
"""
            send_telegram_message(msg)

    if updated:
        try:
            with open(LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to write updated log: {e}")

