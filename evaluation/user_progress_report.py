import json
import os
from typing import Any, Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "user_memory.json")


def load_memory(path: str = MEMORY_FILE) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"topics": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"topics": {}}
        data.setdefault("topics", {})
        return data
    except (json.JSONDecodeError, OSError):
        return {"topics": {}}


def topic_improvement(history: List[Dict[str, Any]]) -> Dict[str, float]:
    if len(history) < 2:
        return {
            "has_delta": False,
            "score_delta": 0.0,
            "accuracy_delta": 0.0,
            "confidence_delta": 0.0,
        }

    first = history[0]
    latest = history[-1]
    return {
        "has_delta": True,
        "score_delta": float(latest.get("score", 0)) - float(first.get("score", 0)),
        "accuracy_delta": float(latest.get("accuracy_pct", 0)) - float(first.get("accuracy_pct", 0)),
        "confidence_delta": float(latest.get("avg_confidence", 0)) - float(first.get("avg_confidence", 0)),
    }


def main() -> None:
    memory = load_memory()
    topics = memory.get("topics", {})

    if not topics:
        print("No user quiz history found at data/user_memory.json")
        return

    print("=== User Progress Evaluation (from saved quiz history) ===")
    improvements = []

    for topic_key, topic_data in sorted(topics.items()):
        name = topic_data.get("display_topic", topic_key)
        history = topic_data.get("quiz_history", [])
        sessions = int(topic_data.get("sessions", 0))

        print(f"\nTopic: {name}")
        print(f"  Sessions: {sessions}")

        if not history:
            print("  No per-attempt history yet")
            continue

        first = history[0]
        latest = history[-1]
        stats = topic_improvement(history)

        print(
            f"  First -> Latest score: {first.get('score', 0)}/{first.get('total', 5)}"
            f" -> {latest.get('score', 0)}/{latest.get('total', 5)}"
        )
        print(
            f"  First -> Latest accuracy: {float(first.get('accuracy_pct', 0)):.1f}%"
            f" -> {float(latest.get('accuracy_pct', 0)):.1f}%"
        )
        print(
            f"  First -> Latest confidence: {float(first.get('avg_confidence', 0)):.2f}/5"
            f" -> {float(latest.get('avg_confidence', 0)):.2f}/5"
        )

        if stats["has_delta"]:
            improvements.append(stats)
            print(f"  Score delta: {stats['score_delta']:+.1f}")
            print(f"  Accuracy delta: {stats['accuracy_delta']:+.1f}%")
            print(f"  Confidence delta: {stats['confidence_delta']:+.2f}")
        else:
            print("  Not enough attempts for improvement delta (need at least 2)")

    if improvements:
        avg_score_delta = sum(x["score_delta"] for x in improvements) / len(improvements)
        avg_accuracy_delta = sum(x["accuracy_delta"] for x in improvements) / len(improvements)
        avg_conf_delta = sum(x["confidence_delta"] for x in improvements) / len(improvements)

        print("\n=== Aggregate Improvement (topics with >=2 attempts) ===")
        print(f"Average score delta: {avg_score_delta:+.2f}")
        print(f"Average accuracy delta: {avg_accuracy_delta:+.2f}%")
        print(f"Average confidence delta: {avg_conf_delta:+.2f}")


if __name__ == "__main__":
    main()
