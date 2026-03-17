import json
import os
from typing import Any, Dict, List

import altair as alt
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "user_memory.json")


def load_memory(path: str = MEMORY_FILE) -> Dict[str, Any]:
    """Load persisted topic history safely from disk."""
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
    """Build sorted concept-level error table for remediation prioritization."""
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
    """Compute first-attempt vs latest-attempt deltas for key outcome signals."""
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


# History page focuses on longitudinal outcomes per topic:
# attempt history, improvement deltas, and concept-level weak spots.
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
                        "confidence_scaled": float(h.get("avg_confidence", 0)) * 20.0,
                    }
                    for i, h in enumerate(history)
                ]
                st.subheader("Progress Trend")
                trend_data = trend_rows
                # Left axis: accuracy percentage.
                accuracy_line = (
                    alt.Chart(alt.Data(values=trend_data))
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("attempt:Q", title="Attempt"),
                        y=alt.Y(
                            "accuracy_pct:Q",
                            title="Accuracy (%)",
                            scale=alt.Scale(domain=[0, 100]),
                        ),
                        color=alt.value("#1f77b4"),
                    )
                )
                # Right axis: confidence 1-5 scaled to 20-100 for shared visual range.
                confidence_line = (
                    alt.Chart(alt.Data(values=trend_data))
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("attempt:Q", title="Attempt"),
                        y=alt.Y(
                            "confidence_scaled:Q",
                            title="Confidence (1-5)",
                            scale=alt.Scale(domain=[0, 100]),
                            axis=alt.Axis(
                                orient="right",
                                values=[20, 40, 60, 80, 100],
                                labelExpr="datum.value / 20",
                            ),
                        ),
                        color=alt.value("#ff7f0e"),
                    )
                )
                st.altair_chart(
                    alt.layer(accuracy_line, confidence_line).resolve_scale(y="independent"),
                    use_container_width=True,
                )
                st.caption(
                    "Legend: Blue line = Accuracy (%). "
                    "Orange line = Confidence x20 (right axis displayed as 1-5)."
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
