from models.evolution import EvolutionSnapshot
from services.llm_service import generate_grounded_text
from services.prompt_engine import build_context

def generate_reflection(snapshot: EvolutionSnapshot, trajectory: dict, strategy_shift: str):
    if not snapshot or trajectory["confidence"] < 0.3:
        return "Not enough data yet to draw strong longitudinal conclusions. Keep logging your states."
        
    basis = [
       f"trajectory_direction:{trajectory['direction']}",
       f"strategy_shift:{strategy_shift}"
    ]

    context = build_context(
        user_state={
            "archetype": snapshot.archetype,
            "stress_avg": snapshot.stress_avg
        },
        signals={
            "trajectory": trajectory,
            "dissonance": snapshot.dissonance,
            "top_strategy": snapshot.top_strategy
        },
        basis=basis
    )

    instruction = "Summarize the past week and highlight 1 key improvement and 1 risk. Maintain a grounded, supportive tone."

    try:
        resp = generate_grounded_text(context, instruction)
        return resp.get("text", "LLM Reflection logic unavailable.")
    except Exception as e:
        trend_arrow = "improving" if trajectory["direction"] == "improving" else "declining"
        return f"""Over the past week:
- Your core stress averaged {(snapshot.stress_avg * 100):.0f}%
- Your behavioral trajectory is currently {trend_arrow}.
- Top Strategy: '{snapshot.top_strategy.replace('_', ' ').capitalize()}'
- Insight: {strategy_shift}"""
