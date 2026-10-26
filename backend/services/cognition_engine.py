import re
from services.llm_service import generate_grounded_text
import json

class CognitionEngine:
    def analyze(self, text: str):
        biases = self.detect_bias(text)
        return {
            "biases": biases,
            "confidence": 0.8
        }

    def detect_bias(self, text: str):
        rule = self.rule_based_bias(text)
        if rule:
            return rule
        return self.llm_bias(text)

    def rule_based_bias(self, text: str):
        biases = []
        if re.search(r"\b(always|never|everyone|no one)\b", text, re.IGNORECASE):
            biases.append({
                "type": "overgeneralization",
                "confidence": 0.8,
                "reframe": "One situation doesn’t define everything."
            })

        if re.search(r"\b(I am useless|I can't)\b", text, re.IGNORECASE):
            biases.append({
                "type": "negative self-belief",
                "confidence": 0.75,
                "reframe": "You’re evaluating yourself too harshly."
            })
        return biases

    def llm_bias(self, text: str):
        context = {
            "state": {},
            "signals": {},
            "basis": [f"text:{text}"]
        }
        res = generate_grounded_text(context, "Detect cognitive bias and suggest a gentle reframe. Output valid JSON: {\"biases\": [{\"type\": \"...\", \"reframe\": \"...\", \"confidence\": 0.8}]}")
        
        t = res.get("text", "")
        try:
            llm_json = json.loads(t) if "{" in t else None
            if llm_json and "biases" in llm_json:
                return llm_json["biases"]
        except Exception:
            pass
        return []

    def analyze_identity_gap(self, intended_actions: int, completed_actions: int, consistency: float, delay: float):
        if intended_actions == 0:
            return {"gap_score": 0, "insight": "Start by setting actionable goals."}
            
        gap_score = 1 - (completed_actions / intended_actions)
        gap_score = max(0.0, min(1.0, gap_score))
        
        insight = "Strong alignment between intentions and reality."
        if gap_score > 0.5:
             insight = "You have significantly more goals than consistent actions."
             
        return {
            "gap_score": gap_score,
            "consistency": consistency,
            "delay": delay,
            "insight": insight
        }

cognition_engine = CognitionEngine()
