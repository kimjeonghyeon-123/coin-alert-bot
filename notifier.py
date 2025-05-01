# notifier.py
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("7570517160:AAHA_GAEzdeY69K7n57Da5QfBRUfgsVbXZQ")
TELEGRAM_CHAT_ID = os.environ.get("7738545441")


def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[알림 실패] 환경변수 미설정")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[텔레그램 오류] {e}")

def send_event_alert(message):
    send_telegram_message(f"📢 이벤트 발생 알림:\n{message}")
