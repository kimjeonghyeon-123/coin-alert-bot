# ... [생략: import 및 상단 코드 동일]

def run_simulation(recent_events: Optional[List[Dict[str, Any]]] = None):
    evaluate_predictions()

    history = get_recent_prices(120)
    if len(history) < 20:
        return

    # 🛠 dict 비교 방지: float 가격만 필터링
    prices = [float(x.get('price')) for x in history if isinstance(x, dict) and isinstance(x.get('price'), (int, float))]
    volumes = [float(x.get('volume', 0)) for x in history if isinstance(x, dict)]
    timestamps = [int(x.get('timestamp', 0)) for x in history if isinstance(x, dict)]

    if len(prices) < 12:
        return

    pattern = detect_chart_pattern(history)
    direction = "long" if prices[-1] > prices[-12] else "short"
    trend = None
    current_time = int(time.time())

    try:
        win_rate, ma5, ma20, ma60 = calculate_probability(
            prices, timestamps, pattern, trend, direction,
            events=recent_events or [], current_time=current_time,
            volumes=volumes
        )
    except Exception as e:
        print("Error in calculate_probability:", e)
        traceback.print_exc()
        return

    entry = prices[-1]
    stop_loss = entry * (0.98 if direction == "long" else 1.02)
    take_profit = entry * (1.02 if direction == "long" else 0.98)

    try:
        message = f"""📊 *시뮬레이션 결과*

*방향:* {direction.capitalize()}
*진입가:* {entry:.2f}
*손절가:* {stop_loss:.2f}
*익절가:* {take_profit:.2f}
*이동평균:* ma5={f"{ma5:.2f}" if ma5 else 'N/A'}, ma20={f"{ma20:.2f}" if ma20 else 'N/A'}, ma60={f"{ma60:.2f}" if ma60 else 'N/A'}
*패턴:* {pattern or '없음'}
*예상 승률:* {win_rate * 100:.1f}%
"""
        send_telegram_message(message)
    except Exception:
        traceback.print_exc()

    prediction = {
        "timestamp": current_time,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "pattern": pattern,
        "trend": trend,
        "win_rate": win_rate,
        "result": None
    }
    save_prediction(prediction)

