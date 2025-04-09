import json
import os
import uuid
from datetime import datetime

LOG_FILE = "simulation_log.json"


def log_simulation_result(sim_result):
    """
    sim_result: dict with keys - timestamp, direction, entry, take_profit,
                                 stop_loss, expected_winrate, pattern, moving_averages, volume_profile
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcfromtimestamp(sim_result["timestamp"]).isoformat(),
        "direction": sim_result["direction"],
        "entry_price": sim_result["entry"],
        "take_profit": sim_result["take_profit"],
        "stop_loss": sim_result["stop_loss"],
        "expected_winrate": sim_result["expected_winrate"],
        "pattern": sim_result.get("pattern"),
        "moving_averages": sim_result.get("moving_averages"),
        "volume_profile": sim_result.get("volume_profile"),
        "evaluated": False,  # 아직 평가되지 않음
        "result": None       # 결과는 나중에 채워짐
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
