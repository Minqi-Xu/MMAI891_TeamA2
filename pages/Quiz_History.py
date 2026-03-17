import json
import os
from typing import Any, Dict, List

import streamlit as st

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


def top_concept_stats(concept_stats: Dict[str, Dict[str, int]], limit: int = 10) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for concept, stat in concept_stats.items():
        seen = int(stat.get("seen", 0))
        wrong = int(stat.get("wrong", 0))
        wrong_rate = round((wrong / seen) * 100, 1) if seen > 0 else 0.0
        rows.append(
            {
                "concept": concept,
                "seen": seen,
                "wrong": wrong,
                "wrong_rate_pct": wrong_rate,
            }
        )
    rows.sort(key=lambda r: (r["wrong"], r["seen"]), reverse=True)
    return rows[:limit]


def compute_improvement(history: List[Dict[str, Any]]) -> Dict[str, float]:
    if len(history) < 2:
        return {
            "score_delta": 0.0,
            "accuracy_delta": 0.0,
            "confidence_delta": 0.0,
            "has_delta": False,
        }

    first = history[0]
    latest = history[-1]
    first_score = float(first.get("score", 0))
    latest_score = float(latest.get("score", 0))
    first_acc = float(first.get("accuracy_pct", 0))
    latest_acc = float(latest.get("accuracy_pct", 0))
    first_conf = float(first.get("avg_confidence", 0))
    latest_conf = float(latest.get("avg_confidence", 0))

    return {
        "score_delta": latest_score - first_score,
        "accuracy_delta": latest_acc - first_acc,
        "confidence_delta": latest_conf - first_conf,
        "has_delta": True,
    }


st.set_page_config(page_title="Quiz History", layout="wide")
st.title("Quiz History by Topic")
st.page_link("app.py", label="Back to Main App")

memory = load_memory()
topics = memory.get("topics", {})

if not topics:
    st.info("No saved quiz history yet. Complete at least one quiz in the main page.")
else:
    st.success(f"Loaded history for {len(topics)} topic(s).")

    # Sort by most sessions first
    sorted_topics = sorted(
        topics.items(),
        key=lambda kv: int(kv[1].get("sessions", 0)),
        reverse=True,
    )

    for topic_key, topic_data in sorted_topics:
        display_topic = topic_data.get("display_topic", topic_key)
        sessions = int(topic_data.get("sessions", 0))
        last_conf = topic_data.get("last_avg_confidence", "N/A")
        last_route = topic_data.get("last_routed_difficulty", "N/A")

        with st.expander(f"{display_topic} | sessions: {sessions}", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("Sessions", str(sessions))
            c2.metric("Last Avg Confidence", str(last_conf))
            c3.metric("Last Route", str(last_route))

            history = topic_data.get("quiz_history", [])
            if history:
                st.subheader("Improvement Summary")
                improvement = compute_improvement(history)

                latest = history[-1]
                first = history[0]
                m1, m2, m3 = st.columns(3)
                m1.metric(
                    "Latest Score",
                    f"{latest.get('score', 0)}/{latest.get('total', 5)}",
                    delta=(
                        f"{improvement['score_delta']:+.1f} vs first"
                        if improvement["has_delta"]
                        else "Not enough history"
                    ),
                )
                m2.metric(
                    "Latest Accuracy",
                    f"{float(latest.get('accuracy_pct', 0)):.1f}%",
                    delta=(
                        f"{improvement['accuracy_delta']:+.1f}% vs first"
                        if improvement["has_delta"]
                        else "Not enough history"
                    ),
                )
                m3.metric(
                    "Latest Confidence",
                    f"{float(latest.get('avg_confidence', 0)):.2f}/5",
                    delta=(
                        f"{improvement['confidence_delta']:+.2f} vs first"
                        if improvement["has_delta"]
                        else "Not enough history"
                    ),
                )

                st.caption(
                    f"First attempt: score {first.get('score', 0)}/{first.get('total', 5)}, "
                    f"accuracy {float(first.get('accuracy_pct', 0)):.1f}%, "
                    f"confidence {float(first.get('avg_confidence', 0)):.2f}/5"
                )

                trend_rows = [
                    {
                        "attempt": i + 1,
                        "accuracy_pct": float(h.get("accuracy_pct", 0)),
                        "score": float(h.get("score", 0)),
                        "avg_confidence": float(h.get("avg_confidence", 0)),
                    }
                    for i, h in enumerate(history)
                ]
                st.subheader("Progress Trend")
                st.line_chart(
                    {
                        "accuracy_pct": [r["accuracy_pct"] for r in trend_rows],
                        "score": [r["score"] for r in trend_rows],
                        "avg_confidence": [r["avg_confidence"] for r in trend_rows],
                    }
                )

                # Newest first for readability in the table.
                history_view = list(reversed(history))
                st.subheader("Previous Quiz Results")
                st.dataframe(history_view, use_container_width=True)
            else:
                st.caption("No per-attempt history stored for this topic yet.")

            concept_stats = top_concept_stats(topic_data.get("concept_stats", {}), limit=10)
            if concept_stats:
                st.subheader("Concept Performance")
                st.dataframe(concept_stats, use_container_width=True)
