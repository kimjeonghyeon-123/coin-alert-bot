import json
import matplotlib.pyplot as plt
import numpy as np

STATS_FILE = "learning_stats.json"
RECENT_WINDOW = 100  # 최근 100건 기준

def load_stats():
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def plot_filtered_pattern_win_rates():
    stats = load_stats()
    patterns = stats.get("patterns", {})

    pattern_names = []
    win_rates = []

    for pattern, result in patterns.items():
        history = result.get("history", [])
        if len(history) < 10:
            continue  # 데이터가 너무 적으면 제외

        recent = history[-RECENT_WINDOW:]
        total = len(recent)
        success = sum(recent)
        win_rate = success / total * 100

        if win_rate < 70:
            continue  # 자동 필터링

        pattern_names.append(pattern)
        win_rates.append(win_rate)

    if not pattern_names:
        print("⚠️ 70% 이상 승률 패턴 없음")
        return

    # 정렬
    sorted_data = sorted(zip(win_rates, pattern_names), reverse=True)
    win_rates, pattern_names = zip(*sorted_data)

    plt.figure(figsize=(12, 6))
    bars = plt.bar(pattern_names, win_rates, color='skyblue')
    plt.axhline(70, color='red', linestyle='--', label='70% 기준선')

    for bar, rate in zip(bars, win_rates):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{rate:.1f}%', ha='center', fontsize=8)

    plt.title("📊 최근 100건 기준 70% 이상 승률 패턴")
    plt.xlabel("패턴명")
    plt.ylabel("승률 (%)")
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_moving_avg_winrate(pattern_name, window=20):
    stats = load_stats()
    pattern = stats.get("patterns", {}).get(pattern_name)
    if not pattern:
        print(f"패턴 '{pattern_name}' 없음")
        return

    history = pattern.get("history", [])
    if len(history) < window:
        print(f"패턴 '{pattern_name}'의 데이터가 부족합니다")
        return

    history_array = np.array(history)
    moving_avg = np.convolve(history_array, np.ones(window)/window, mode='valid')

    plt.figure(figsize=(10, 4))
    plt.plot(moving_avg * 100, label=f"{pattern_name} - {window}건 이동 평균")
    plt.axhline(70, color='red', linestyle='--', label='70% 기준선')
    plt.title(f"📈 {pattern_name} 패턴의 이동 평균 승률")
    plt.xlabel("최근 시도")
    plt.ylabel("이동 평균 승률 (%)")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_filtered_pattern_win_rates()

    # 이동 평균 그래프 보고 싶은 패턴 수동 입력 (예시)
    plot_moving_avg_winrate("HeadAndShoulders", window=20)
    plot_moving_avg_winrate("DoubleBottom", window=20)
