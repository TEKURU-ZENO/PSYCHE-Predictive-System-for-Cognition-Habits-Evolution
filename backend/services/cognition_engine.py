"""
Psych-AI Platform - Clinical Cognitive Distortion Analysis Engine
Implements evidence-based Cognitive Behavioral Therapy (CBT) distortion classification,
Socratic reality-testing prompts, and empathetic cognitive reframing with safety circuit breakers.
"""

import re
import json
from typing import Dict, Any, List, Optional
from services.crisis_service import CrisisService
from services.llm_service import generate_grounded_text

# Recognized Cognitive Behavioral Therapy (CBT) distortion categories with rich linguistic signals
CBT_TAXONOMY = {
    "all_or_nothing": {
        "name": "All-or-Nothing Thinking (Dichotomous)",
        "patterns": [
            r"\b(?:always|never|completely|totally|entirely|ruined|total\s+failure|complete\s+disaster|everything\s+is\s+lost)\b",
            r"\b(?:either|or)\s+(?:perfect|nothing)\b",
            r"\b100%\s+(?:ruined|hopeless|pointless)\b"
        ],
        "default_reframe": "Situations are rarely entirely black-or-white. Consider where this falls on a continuum of grey.",
        "socratic_question": "Is it possible for parts of this to be challenging while other parts are manageable or successful?"
    },
    "overgeneralization": {
        "name": "Overgeneralization",
        "patterns": [
            r"\b(?:everyone|nobody|no\s*one|everybody)\s+(?:always|never|hates|ignores|leaves)\b",
            r"\b(?:every\s+single\s+time|without\s+fail|it\s+never\s+works)\b",
            r"\bI\s+will\s+never\s+(?:be|succeed|pass|finish|change)\b"
        ],
        "default_reframe": "A single difficult event or isolated setback does not define an ongoing, permanent pattern.",
        "socratic_question": "Can you recall a time or context where this was not the case?"
    },
    "catastrophizing": {
        "name": "Catastrophizing (Magnification)",
        "patterns": [
            r"\b(?:end\s+of\s+the\s+world|my\s+life\s+is\s+over|career\s+is\s+ruined|worst\s+(?:thing|nightmare))\b",
            r"\b(?:unbearable|unlivable|cannot\s+survive\s+this|beyond\s+repair)\b"
        ],
        "default_reframe": "This is genuinely stressful, but rarely does one event represent an absolute, unrecoverable catastrophe.",
        "socratic_question": "If the worst-case scenario were to happen, what specific actions could you take to navigate through it?"
    },
    "mind_reading": {
        "name": "Mind Reading (Jumping to Conclusions)",
        "patterns": [
            r"\b(?:they|everyone|people)\s+(?:think|know|believe)\s+I(?:'m|\s+am)\s+(?:an?\s+)?(?:idiot|stupid|fake|incompetent|lazy)\b",
            r"\bI\s+know\s+(?:they|he|she)\s+(?:hates?|judg(?:es?|ing)|laughs?\s+at)\s+me\b",
            r"\bthey\s+all\s+despise\s+me\b"
        ],
        "default_reframe": "We often project our own self-criticisms onto what we imagine others are thinking without objective proof.",
        "socratic_question": "What concrete, observable facts tell you what the other person is thinking right now?"
    },
    "fortune_telling": {
        "name": "Fortune Telling (Negative Prediction)",
        "patterns": [
            r"\bI\s+(?:just\s+)?know\s+(?:I\s+will\s+fail|it\s+will\s+fail|it\s+won(?:'t|\s+not)\s+work)\b",
            r"\b(?:bound|doomed)\s+to\s+fail\b",
            r"\bthere\s+is\s+no\s+point\s+in\s+trying\b"
        ],
        "default_reframe": "Anticipating difficulty helps us prepare, but predicting failure as a guaranteed certainty limits our agency.",
        "socratic_question": "What is the most likely, realistic outcome rather than the worst possible projection?"
    },
    "emotional_reasoning": {
        "name": "Emotional Reasoning",
        "patterns": [
            r"\bI\s+feel\s+(?:like\s+a\s+)?(?:failure|loser|fraud|incompetent)\s*,?\s*so\s+I\s+must\s+be\b",
            r"\bI\s+feel\s+(?:it|hopeless|worthless)\s*,?\s*so\s+it\s+(?:must\s+be|is)\s+true\b",
            r"\bmy\s+feelings\s+prove\s+that\b"
        ],
        "default_reframe": "Emotions are valid subjective experiences, but feeling like something is true does not make it an objective reality.",
        "socratic_question": "If you set feelings aside for a moment, what do the external facts say?"
    },
    "should_statements": {
        "name": "Should / Must Statements (Imperatives)",
        "patterns": [
            r"\bI\s+(?:should|must|ought\s+to|have\s+to)\s+(?:have\s+known|never\s+make|be\s+perfect|do\s+better|be\s+stronger)\b",
            r"\bI\s+shouldn(?:'t|\s+not)\s+feel\s+(?:this\s+way|tired|sad|weak)\b"
        ],
        "default_reframe": "Rigid 'should' rules create unnecessary guilt and shame. Try replacing 'I should' with 'I would prefer to'.",
        "socratic_question": "What standard would you hold a close friend or colleague to in this exact same situation?"
    },
    "labeling": {
        "name": "Labeling and Mislabeling",
        "patterns": [
            r"\bI(?:'m|\s+am)\s+(?:an?\s+)?(?:total\s+|complete\s+|real\s+|absolute\s+)?(?:loser|failure|idiot|fraud|imposter|useless|worthless|screw[\s\-]*up|terrible\s+person)\b",
            r"\bI(?:'m|\s+am)\s+such\s+a\s+mess\b",
            r"\b(?:a\s+total\s+loser|a\s+complete\s+failure)\b"
        ],
        "default_reframe": "You made a mistake or are encountering difficulty; that is an event, not your core personal identity.",
        "socratic_question": "Can you describe the specific behavior or hurdle without using a global label on your character?"
    },
    "disqualifying_positive": {
        "name": "Disqualifying the Positive",
        "patterns": [
            r"\b(?:they\s+only\s+said\s+that|they\s+were\s+just\s+being\s+nice)\b",
            r"\b(?:pure|just|dumb)\s+luck\b",
            r"\bthat\s+doesn(?:'t|\s+not)\s+count\b",
            r"\banyone\s+could\s+have\s+done\s+(?:that|it)\b"
        ],
        "default_reframe": "Acknowledging positive feedback and real accomplishments does not mean you are arrogant; it is honest accounting.",
        "socratic_question": "Why does this positive accomplishment not count? What would make it count?"
    },
    "personalization": {
        "name": "Personalization (Excessive Self-Blame)",
        "patterns": [
            r"\b(?:it(?:'s|\s+is)\s+all\s+my\s+fault|everything\s+is\s+my\s+fault)\b",
            r"\bI\s+ruined\s+(?:everything|their\s+day|the\s+event|the\s+meeting)\b",
            r"\bif\s+only\s+I\s+hadn(?:'t|\s+not)\s+been\s+there\b"
        ],
        "default_reframe": "Outcomes are shaped by many intersecting factors and people, rarely a single person alone.",
        "socratic_question": "What other variables, people, or constraints contributed to this outcome besides you?"
    }
}


class CognitionEngine:
    """
    Cognitive processing engine analyzing thought journals and user scenarios for
    cognitive distortions, emotional dissonance, and identity alignment.
    """

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze user text for crisis signals and cognitive distortions.
        Prioritizes crisis safety checks before any cognitive reframing.
        """
        if not text or not isinstance(text, str):
            return {
                "biases": [],
                "confidence": 0.0,
                "is_crisis": False
            }

        # 1. Mandatory Crisis Circuit Breaker
        crisis_check = CrisisService.evaluate(text)
        if crisis_check["is_crisis"]:
            return {
                "is_crisis": True,
                "severity": crisis_check["severity"],
                "crisis_response": crisis_check["response"],
                "biases": [],
                "confidence": 1.0,
                "notice": "Cognitive analysis suspended: immediate human support resources provided."
            }

        # 2. Extract Candidate Distortions via Clinical CBT Heuristic Rules
        heuristic_biases = self.rule_based_bias(text)

        # 3. Enhance / Contextualize via LLM Semantic Reasoning
        final_biases = self.llm_enhanced_bias(text, heuristic_biases)

        return {
            "is_crisis": False,
            "biases": final_biases,
            "confidence": 0.85 if final_biases else 0.70,
            "distortion_count": len(final_biases)
        }

    def rule_based_bias(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans text against the comprehensive 10-class CBT distortion taxonomy.
        Extracts matched spans, clinical classifications, Socratic questions, and reframes.
        """
        detected = []
        lower = text.lower()

        for category_key, category in CBT_TAXONOMY.items():
            for pat in category["patterns"]:
                match = re.search(pat, lower, re.IGNORECASE)
                if match:
                    span_start, span_end = match.span()
                    matched_text = text[span_start:span_end]

                    # Prevent duplicate categories in single text
                    if not any(d["type"] == category["name"] for d in detected):
                        detected.append({
                            "type": category["name"],
                            "category_key": category_key,
                            "quote": matched_text,
                            "confidence": 0.85,
                            "reframe": category["default_reframe"],
                            "socratic_question": category["socratic_question"]
                        })
                    break

        return detected

    def llm_enhanced_bias(self, text: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Synthesizes rule-based candidate evidence with semantic LLM inference for
        personalized Socratic inquiries and nuanced cognitive reframing.
        """
        # If candidate list is comprehensive and LLM is in offline fallback, return candidate list
        prompt = (
            f"You are a clinical CBT cognitive assistant. Analyze this journal thought:\n\"{text}\"\n"
            f"Identified preliminary distortion signals: {[c['type'] for c in candidates]}.\n"
            "Return valid JSON adhering to schema:\n"
            "{\"biases\": [{\"type\": \"<CBT Distortion Name>\", \"quote\": \"<exact phrase>\", \"reframe\": \"<balanced empathetic reframe>\", \"socratic_question\": \"<reality-testing question>\", \"confidence\": 0.85}]}"
        )

        context = {
            "state": {"text": text},
            "signals": {
                "candidates": [c["type"] for c in candidates],
                "raw_candidates": candidates
            },
            "basis": [f"candidate_count:{len(candidates)}"]
        }

        try:
            res = generate_grounded_text(context, prompt)
            raw = res.get("text", "")
            
            # Extract JSON block
            json_str = raw
            if "```json" in raw:
                json_str = raw.split("```json")[1].split("```")[0].strip()
            elif "{" in raw and "}" in raw:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                json_str = raw[start:end]

            parsed = json.loads(json_str)
            if isinstance(parsed, dict) and "biases" in parsed and isinstance(parsed["biases"], list):
                llm_biases = parsed["biases"]
                if llm_biases:
                    # Validate each entry
                    cleaned = []
                    for b in llm_biases:
                        cleaned.append({
                            "type": b.get("type", "Cognitive Distortion"),
                            "quote": b.get("quote", text[:40]),
                            "reframe": b.get("reframe", "Consider looking at this from another perspective."),
                            "socratic_question": b.get("socratic_question", "What evidence supports or contradicts this thought?"),
                            "confidence": float(b.get("confidence", 0.85))
                        })
                    return cleaned
        except Exception:
            pass

        # Robust fallback: return the clinical heuristic candidates
        return candidates

    def analyze_identity_gap(self, intended_actions: int, completed_actions: int, consistency: float, delay: float) -> Dict[str, Any]:
        """
        Quantifies the gap between stated intentions and actual behavioral follow-through.
        """
        if intended_actions <= 0:
            return {"gap_score": 0.0, "insight": "Start by setting actionable micro-goals."}

        gap_score = 1.0 - (completed_actions / max(1, intended_actions))
        gap_score = max(0.0, min(1.0, gap_score))

        insight = "Strong alignment between intentions and reality."
        if gap_score > 0.6:
            insight = "Significant dissonance between stated intentions and consistent follow-through."
        elif gap_score > 0.3:
            insight = "Moderate friction: focus on reducing initiation hurdles for key intentions."

        return {
            "gap_score": round(gap_score, 2),
            "consistency": round(consistency, 2),
            "delay": round(delay, 2),
            "insight": insight
        }


cognition_engine = CognitionEngine()
