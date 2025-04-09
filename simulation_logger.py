import json
import os
import uuid
import time
from datetime import datetime
from price_logger import get_current_price
from notifier import send_telegram_message

LOG_FILE = "simulation_log.json"
LEARNING_FILE = "learning_stats.json"


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
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Logging simulation result failed: {e}")


def update_learning_stats(direction, trend, pattern, result):
    """
    direction: 'long' or 'short'
    trend: 'up', 'down', or None
    pattern: chart pattern name or None
    result: 'success' or 'fail'
    """
    path = LEARNING_FILE

    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                stats = json.load(f)
        else:
            stats = {"direction": {}, "trend": {}, "patterns": {}}
    except:
        stats = {"direction": {}, "trend": {}, "patterns": {}}

    # Direction
    if direction not in stats["direction"]:
        stats["direction"][direction] = {"success": 0, "fail": 0}
    stats["direction"][direction][result] += 1

    # Trend
    if trend:
        if trend not in stats["trend"]:
            stats["trend"][trend] = {"success": 0, "fail": 0}
        stats["trend"][trend][result] += 1

    # Pattern
    if pattern:
        if pattern not in stats["patterns"]:
            stats["patterns"][pattern] = {"success": 0, "fail": 0}
        stats["patterns"][pattern][result] += 1

    try:
        with open(path, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to write learning stats: {e}")


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
        if elapsed < 1800:  # 평가까지 최소 30분 대기
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
        else:  # short
            if current_price <= tp:
                result = "success"
            elif current_price >= sl:
                result = "fail"

        if result:
            log["evaluated"] = True
            log["result"] = result
            updated = True

            # 자동 학습 업데이트
            trend = None
            ma = log.get("moving_averages", {})
            if ma:
                if ma.get("ma5") > ma.get("ma20") > ma.get("ma60"):
                    trend = "up"
                elif ma.get("ma5") < ma.get("ma20") < ma.get("ma60"):
                    trend = "down"

            update_learning_stats(
                direction=direction,
                trend=trend,
                pattern=log.get("pattern"),
                result=result
            )

            msg = f"""📘 *시뮬레이션 평가 결과*
*방향:* {direction.upper()}
*진입가:* {log['entry_price']:.2f}
*TP / SL:* {tp:.2f} / {sl:.2f}
*현재가:* {current_price:.2f}
*패턴:* {log.get('pattern', '없음')}
*예상 승률:* {log.get('expected_winrate', 0)}%
*추세:* {trend or '판단불가'}
*결과:* {'✅ 익절 성공' if result == 'success' else '❌ 손절 실패'}
"""
            send_telegram_message(msg)

    if updated:
        try:
            with open(LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to write updated log: {e}")
