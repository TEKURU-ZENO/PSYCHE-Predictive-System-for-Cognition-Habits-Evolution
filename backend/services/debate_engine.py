import json
from services.llm_service import call_llm

def run_debate(agent_outputs):
    arguments = []
    
    # 2.4 AGENT ROLE PROMPTS lens mapping
    role_lens = {
        "prediction": "forecast risk strictly",
        "strategy": "maximize long-term outcome",
        "meta": "ensure identity and core goal alignment",
        "cognition": "detect narrative bias and unblock execution"
    }

    for agent, data in agent_outputs.items():
        if agent in ["state", "weights", "confidence", "prediction", "strategy", "meta", "cognition"]:
            if agent in role_lens:
                # Re-map standard responses under role constraints
                output = data.get("output", {})
                if output:
                    arguments.append({
                        "agent": agent,
                        "perspective": role_lens[agent],
                        "position": output,
                        "confidence": data.get("confidence", 0.0)
                    })

    return arguments

def synthesize_debate(arguments):
    prompt = f"""
Agents have produced the following competing perspectives:
{json.dumps(arguments, indent=2)}

You are the Synthesizer. Reconcile this debate into a single structured output.
Rules:
- Do NOT ignore any agent. You must assess every perspective.
- If conflict exists, explicitly mention it.
- Final decision must reference at least 2 agents weighing against one another.
- Be grounded in the inputs only. Do not invent details. Provide valid JSON only:

{{
  "final_decision": "string (the ultimate action)",
  "reasoning": "string (detailed explanation of how inputs were weighted)",
  "conflicts_detected": ["list of strings detailing disagreements (if any)"],
  "confidence": float (0.0 to 1.0)
}}
"""
    try:
        # Wrap the LLM call directly to bypass standard contextual prompt engine constraints
        res = call_llm(prompt, temperature=0.4)
        t = res.get("text", "{}")
        synthesis = json.loads(t) if "{" in t else None
        
        if synthesis and "final_decision" in synthesis:
            return synthesis
            
    except Exception as e:
        pass

    return {
        "final_decision": "Standard deterministic fallback",
        "reasoning": "LLM Synthesis temporarily unavailable. Relying on deterministic aggregator.",
        "conflicts_detected": [],
        "confidence": 0.0
    }
