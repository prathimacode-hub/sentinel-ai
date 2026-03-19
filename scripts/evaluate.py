import random
from collections import defaultdict

# Simulated predictions vs ground truth
CLASSES = [
    "normal", "phone_usage", "multiple_faces", "no_face",
    "looking_away", "book_usage", "impersonation",
    "obstruction", "audio_cheating", "tab_switch"
]


def simulate_predictions(n=100):
    results = []

    for _ in range(n):
        true = random.choice(CLASSES)

        # Simulate 80% accuracy
        pred = true if random.random() < 0.8 else random.choice(CLASSES)

        results.append((true, pred))

    return results


def evaluate(results):
    correct = 0
    total = len(results)

    class_stats = defaultdict(lambda: {"tp": 0, "total": 0})

    for true, pred in results:
        class_stats[true]["total"] += 1

        if true == pred:
            correct += 1
            class_stats[true]["tp"] += 1

    accuracy = correct / total

    print("\n📊 OVERALL ACCURACY:", round(accuracy * 100, 2), "%")

    print("\n📊 CLASS-WISE ACCURACY:")
    for cls in CLASSES:
        tp = class_stats[cls]["tp"]
        total_cls = class_stats[cls]["total"]
        acc = tp / total_cls if total_cls else 0

        print(f"{cls}: {round(acc*100,2)}%")


if __name__ == "__main__":
    results = simulate_predictions(200)
    evaluate(results)
