import random
from dataclasses import dataclass


@dataclass
class SimResult:
    mode: str
    avg_score_round1: float
    avg_score_round2: float
    avg_improvement: float


# Synthetic simulation: a learner performs better when the second round matches current ability.
def simulate_student_round(score_bias: float) -> int:
    score = 0
    for _ in range(5):
        if random.random() < score_bias:
            score += 1
    return score


def run_simulation(n: int = 100, seed: int = 42):
    random.seed(seed)
    static_improvements = []
    adaptive_improvements = []
    static_r1 = []
    static_r2 = []
    adaptive_r1 = []
    adaptive_r2 = []

    for _ in range(n):
        # Round 1 baseline ability
        base_bias = random.uniform(0.35, 0.75)
        r1 = simulate_student_round(base_bias)

        # Static system: always same difficulty => small learning gain
        static_next_bias = min(base_bias + 0.03, 0.9)
        r2_static = simulate_student_round(static_next_bias)

        # Adaptive system: adjusts next round to learner level
        if r1 <= 2:
            adaptive_next_bias = min(base_bias + 0.10, 0.9)
        elif r1 == 3:
            adaptive_next_bias = min(base_bias + 0.06, 0.9)
        else:
            adaptive_next_bias = min(base_bias + 0.05, 0.95)
        r2_adaptive = simulate_student_round(adaptive_next_bias)

        static_r1.append(r1)
        static_r2.append(r2_static)
        adaptive_r1.append(r1)
        adaptive_r2.append(r2_adaptive)
        static_improvements.append(r2_static - r1)
        adaptive_improvements.append(r2_adaptive - r1)

    static = SimResult(
        mode="Static quiz baseline",
        avg_score_round1=sum(static_r1) / n,
        avg_score_round2=sum(static_r2) / n,
        avg_improvement=sum(static_improvements) / n,
    )
    adaptive = SimResult(
        mode="Adaptive agent",
        avg_score_round1=sum(adaptive_r1) / n,
        avg_score_round2=sum(adaptive_r2) / n,
        avg_improvement=sum(adaptive_improvements) / n,
    )
    return static, adaptive


def main():
    static, adaptive = run_simulation()
    print("=== Synthetic Evaluation (n=100) ===")
    for r in [static, adaptive]:
        print(f"Mode: {r.mode}")
        print(f"  Avg Round 1 Score: {r.avg_score_round1:.2f}/5")
        print(f"  Avg Round 2 Score: {r.avg_score_round2:.2f}/5")
        print(f"  Avg Improvement : {r.avg_improvement:.2f} points")

    delta = adaptive.avg_improvement - static.avg_improvement
    print(f"\nAdaptive uplift vs baseline: {delta:+.2f} points")


if __name__ == "__main__":
    main()
