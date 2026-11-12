from collections import OrderedDict
import os
import json
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from services.safety_filter import sanitize

MAX_CACHE_SIZE = 256
PROMPT_CACHE: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


def _cache_set(key: str, value: Dict[str, Any]) -> None:
    if key in PROMPT_CACHE:
        PROMPT_CACHE.move_to_end(key)
    PROMPT_CACHE[key] = value
    if len(PROMPT_CACHE) > MAX_CACHE_SIZE:
        PROMPT_CACHE.popitem(last=False)


def _call_live_llm(prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
    """Calls OpenAI-compatible completion endpoint via standard library."""
    req_data = json.dumps({
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a specialized psychological twin deliberator. Output strict JSON when requested."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    req = urllib.request.Request(
        f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions",
        data=req_data,
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=8) as response:
        resp_json = json.loads(response.read().decode("utf-8"))
        content = resp_json["choices"][0]["message"]["content"]
        return {
            "text": content,
            "confidence": 0.88
        }


def _generate_structured_fallback(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generates deterministic, schema-compliant JSON structures when running without
    external LLM keys (offline development, CI/CD, tests).
    """
    prompt_lower = prompt.lower()
    ctx = context or {}

    # 1. Synthesis / Debate Fusion Prompt
    if "final_decision" in prompt_lower:
        has_push = "push" in prompt_lower
        has_burnout = "burnout" in prompt_lower or "fatigue" in prompt_lower or "risk" in prompt_lower

        conflicts = []
        if has_push and has_burnout:
            conflicts.append("Prediction risk forecast conflicts with Strategy aggressive execution.")
            decision = "Paced Refractory Reset & Task Segmentation"
            reasoning = "PredictionAgent identified acute burnout risk, overriding direct push-through in favor of structured pacing."
            conf = 0.86
        else:
            decision = "Adaptive Task Chunking with 15m Focus Blocks"
            reasoning = "Reconciled Strategy and Cognition inputs: established manageable milestones preserving cognitive clarity."
            conf = 0.89

        synthesis_json = json.dumps({
            "final_decision": decision,
            "reasoning": reasoning,
            "conflicts_detected": conflicts,
            "confidence": conf
        })
        return {
            "text": synthesis_json,
            "confidence": conf
        }

    # 2. Cognition Biases Prompt
    if "detect cognitive bias" in prompt_lower or '"biases"' in prompt_lower:
        raw_candidates = ctx.get("signals", {}).get("raw_candidates", [])
        if raw_candidates:
            return {
                "text": json.dumps({"biases": raw_candidates}),
                "confidence": 0.85
            }

        candidates = ctx.get("signals", {}).get("candidates", [])
        detected = []
        if candidates:
            for c in candidates:
                detected.append({
                    "type": c,
                    "reframe": "Consider looking at this from another perspective.",
                    "socratic_question": "What evidence supports or contradicts this conclusion?",
                    "confidence": 0.85
                })
        else:
            if any(w in prompt_lower for w in ["always", "never", "everyone", "nobody", "no one"]):
                detected.append({
                    "type": "Overgeneralization",
                    "reframe": "One challenging milestone does not define your total trajectory.",
                    "socratic_question": "Can you recall a time where this did not occur?",
                    "confidence": 0.82
                })
            if any(w in prompt_lower for w in ["useless", "failing", "can't", "impossible", "loser"]):
                detected.append({
                    "type": "Catastrophizing",
                    "reframe": "Break the immediate problem into observable, bite-sized components.",
                    "socratic_question": "What is the most likely realistic outcome?",
                    "confidence": 0.85
                })
        return {
            "text": json.dumps({"biases": detected}),
            "confidence": 0.85 if detected else 0.70
        }

    # 3. Simulation Projections Prompt
    if "thoughts" in prompt_lower and "risks" in prompt_lower:
        sim_json = json.dumps({
            "thoughts": ["Evaluate immediate priorities and isolate the core bottleneck."],
            "actions": ["Execute a 15-minute refractory block before resuming analytical review."],
            "risks": ["Context switching without closure accelerates afternoon fatigue."],
            "outcomes": ["Preserves executive function while sustaining deliberate progress."]
        })
        return {
            "text": sim_json,
            "confidence": 0.84
        }

    # 4. Standard Reflection / Grounded Summary
    return {
        "text": json.dumps({
            "text": "Over the observed window, cognitive reserves have demonstrated resilient adaptation. Prioritizing structured refractory breaks continues to produce favorable emotional stability.",
            "confidence": 0.85
        }),
        "confidence": 0.85
    }


def call_llm(prompt: str, temperature: float = 0.3, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cache_key = hashlib.sha256(f"{prompt}_{temperature}".encode('utf-8')).hexdigest()
    if cache_key in PROMPT_CACHE:
        PROMPT_CACHE.move_to_end(cache_key)
        return PROMPT_CACHE[cache_key]

    if OPENAI_API_KEY:
        try:
            res = _call_live_llm(prompt, temperature)
            _cache_set(cache_key, res)
            return res
        except Exception as e:
            print(f"Warning: Live LLM call failed ({e}). Utilizing structured engine fallback.")

    res = _generate_structured_fallback(prompt, context=context)
    _cache_set(cache_key, res)
    return res


def build_prompt(context: Dict[str, Any], instruction: str) -> str:
    return f"""
You are a careful, non-judgmental assistant.

GROUND TRUTH (do not invent facts):
{json.dumps(context, indent=2)}

INSTRUCTIONS:
- Use only the ground truth.
- Be concise (3–5 sentences).
- Use probabilistic language (may, tends to).
- Do NOT diagnose.
- Explain clearly for a user.

TASK:
{instruction}

OUTPUT (JSON ONLY):
{{
  "text": "...",
  "confidence": 0.0
}}
"""


def generate_grounded_text(context: Dict[str, Any], instruction: str) -> Dict[str, Any]:
    prompt = build_prompt(context, instruction)
    try:
        resp = call_llm(prompt, context=context)
        raw_text = resp.get("text", "")
        if isinstance(raw_text, str) and raw_text.strip().startswith("{"):
            try:
                parsed = json.loads(raw_text)
                if "text" in parsed:
                    resp = {**resp, "text": parsed["text"]}
            except Exception:
                pass

        safe_resp = sanitize(dict(resp), resp.get("confidence", 0.0))
        return safe_resp
    except Exception:
        return {"text": "LLM generation unavailable. Utilizing foundational engine output.", "confidence": 0.0}
