import json
import matplotlib.pyplot as plt

STATS_FILE = "learning_stats.json"

def load_stats():
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def plot_pattern_win_rates():
    stats = load_stats()
    patterns = stats.get("patterns", {})

    pattern_names = []
    win_rates = []

    for pattern, result in patterns.items():
        total = result["success"] + result["fail"]
        if total == 0:
            continue
        win_rate = result["success"] / total
        pattern_names.append(pattern)
        win_rates.append(win_rate * 100)

    # 정렬 (승률 높은 순으로)
    sorted_data = sorted(zip(win_rates, pattern_names), reverse=True)
    win_rates, pattern_names = zip(*sorted_data)

    # 시각화
    plt.figure(figsize=(12, 6))
    bars = plt.bar(pattern_names, win_rates, color='skyblue')
    plt.axhline(70, color='red', linestyle='--', label='70% 기준선')

    for bar, rate in zip(bars, win_rates):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{rate:.1f}%', ha='center', fontsize=8)

    plt.title("📊 패턴별 승률 시각화")
    plt.xlabel("패턴명")
    plt.ylabel("승률 (%)")
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_pattern_win_rates()
