import requests

# ✅ 직접 지정한 텔레그램 봇 토큰과 채팅 ID
TELEGRAM_BOT_TOKEN = "7570517160:AAHA_GAEzdeY69K7n57Da5QfBRUfgsVbXZQ"
TELEGRAM_CHAT_ID = "7738545441"


def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[알림 실패] 텔레그램 토큰 또는 챗 ID 없음")
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


def send_event_alert(event):
    """
    event는 dict 형태여야 함:
    {
        'summary': str,
        'impact': str,
        'source': str,
        'url': Optional[str]
    }
    """
    try:
        summary = event.get("summary", "설명 없음")
        impact = event.get("impact", "영향도 정보 없음")
        source = event.get("source", "출처 미확인")
        url = event.get("url")

        msg = f"📢 *이벤트 발생!*\n" \
              f"📝 {summary}\n" \
              f"💥 영향도: *{impact}*\n" \
              f"🔗 출처: {source}"

        if url:
            msg += f"\n🌐 [상세보기]({url})"

        send_telegram_message(msg)
    except Exception as e:
        print(f"[이벤트 알림 실패] {e}")

