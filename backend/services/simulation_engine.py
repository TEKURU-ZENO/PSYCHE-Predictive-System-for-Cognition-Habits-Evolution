from services.llm_service import generate_grounded_text
from services.prompt_engine import build_context
import json

def simulate_scenario(scenario: str, user_state: dict):
    emotion = user_state.get("emotion")
    triggers = user_state.get("triggers", [])
    
    # Mocking an RL summary constraint based on existing playbook
    rl_summary = {"top_action": "take a break (simulated)"}

    basis = [
        f"scenario:{scenario}",
        *[f"trigger:{t['event']}→{t['emotion']}" for t in triggers],
        f"rl_top:{rl_summary.get('top_action')}"
    ]

    context = build_context(
        user_state=user_state,
        signals={"triggers": triggers, "rl": rl_summary},
        basis=basis
    )

    instruction = """
    Given the scenario, produce psychological projections based STRICTLY on the basis arrays.
    Include 1-2 points per list. Return clean raw JSON:
    {
      "thoughts": ["..."],
      "actions": ["..."],
      "risks": ["..."],
      "outcomes": ["..."]
    }
    """

    try:
        resp = generate_grounded_text(context, instruction)
        text = resp.get("text", "{}")
        # Ensure it's coercible into JSON, naive clean up since mock could return flat text 
        # (This protects against mock raw strings vs true LLM json strings)
        llm_json = json.loads(text) if "{" in text else None
        if llm_json and "thoughts" in llm_json:
            return llm_json
    except Exception as e:
        pass

    # Deterministic Fallback if LLM parsing fails
    response = {
        "thoughts": [],
        "actions": [],
        "risks": [],
        "outcomes": []
    }

    scenario_lower = scenario.lower()
    if "deadline" in scenario_lower and (emotion == "stressed" or emotion == "fatigued"):
        response["thoughts"].append("This feels overwhelming.")
        response["actions"].append("Delay starting or overthink.")
        response["risks"].append("Last-minute rush.")
        response["outcomes"].append("Reduced quality work.")
    else:
        response["thoughts"].append("I need to formulate a plan.")
        response["actions"].append("Take it one step at a time.")
        response["outcomes"].append("Standard execution.")

    for t in triggers:
        if t["event"] in scenario_lower:
            response["risks"].append(f"Pattern repetition detected: {t['event']} frequently leads to {t['emotion']}.")

    return response
