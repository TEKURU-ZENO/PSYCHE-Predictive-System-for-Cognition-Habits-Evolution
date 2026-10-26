import os
import json
import hashlib
from typing import Dict, Any
from services.safety_filter import sanitize

PROMPT_CACHE = {}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def call_llm(prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
    cache_key = hashlib.sha256(f"{prompt}_{temperature}".encode('utf-8')).hexdigest()
    if cache_key in PROMPT_CACHE:
        return PROMPT_CACHE[cache_key]

    # MVP Mock Response until active integration
    mock_payload = {
        "text": "Based on the trailing metrics and recent behavioral shifts, you are demonstrating consistent adaptive resilience, though stress triggers still occasionally map to friction responses.",
        "confidence": 0.82
    }
    
    PROMPT_CACHE[cache_key] = mock_payload
    return mock_payload

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
        resp = call_llm(prompt)
        safe_resp = sanitize(resp, resp.get("confidence", 0.0))
        return safe_resp
    except Exception as e:
        return {"text": "LLM generation unavailable. Utilizing foundational engine output.", "confidence": 0.0}
