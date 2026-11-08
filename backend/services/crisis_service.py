"""
Psych-AI Platform - Clinical Crisis Detection & Emergency Safety Service
Ethical Circuit Breaker for Self-Harm, Suicidal Ideation, and Acute Psychological Emergencies.

CRITICAL DIRECTIVE:
When an acute crisis is detected, normal AI generation, coaching, cognitive challenging,
and productivity optimization MUST IMMEDIATELY HALT. The system acts as a protective
circuit breaker, returning verified, accessible, free, and confidential human crisis resources.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# Vetted, free, confidential 24/7 crisis helplines and resources
CRISIS_HELPLINES = [
    {
        "name": "988 Suicide & Crisis Lifeline",
        "region": "United States & Canada",
        "contact": "988",
        "type": "call_or_text",
        "action_url": "tel:988",
        "web_url": "https://988lifeline.org",
        "description": "Free, confidential, 24/7 support for anyone in distress, prevention, and crisis resources."
    },
    {
        "name": "Crisis Text Line",
        "region": "US, UK, Canada",
        "contact": "Text HOME to 741741",
        "type": "text",
        "action_url": "sms:741741?body=HOME",
        "web_url": "https://www.crisistextline.org",
        "description": "Free 24/7 support from a trained crisis counselor over SMS text."
    },
    {
        "name": "The Trevor Project",
        "region": "LGBTQ Youth (US)",
        "contact": "1-866-488-7386 or Text START to 678-678",
        "type": "call_or_text",
        "action_url": "tel:18664887386",
        "web_url": "https://www.thetrevorproject.org",
        "description": "24/7 confidential suicide prevention and crisis intervention for LGBTQ young people."
    },
    {
        "name": "Veterans Crisis Line",
        "region": "United States",
        "contact": "Dial 988, then press 1 (or Text 838255)",
        "type": "call_or_text",
        "action_url": "tel:988",
        "web_url": "https://www.veteranscrisisline.net",
        "description": "24/7 confidential crisis line connecting veterans in crisis and their families."
    },
    {
        "name": "Samaritans & NHS 111",
        "region": "United Kingdom",
        "contact": "Call 116 123 (Samaritans) or 111 (NHS)",
        "type": "call",
        "action_url": "tel:116123",
        "web_url": "https://www.samaritans.org",
        "description": "Free 24/7 round-the-clock emotional support across the UK."
    },
    {
        "name": "Befrienders Worldwide & Find A Helpline",
        "region": "International / Worldwide (130+ countries)",
        "contact": "findahelpline.com",
        "type": "directory",
        "action_url": "https://findahelpline.com",
        "web_url": "https://findahelpline.com",
        "description": "Free, confidential directory of local crisis lines and emergency support worldwide."
    }
]

# High-sensitivity clinical regex patterns for self-harm and suicide ideation
EXPLICIT_SUICIDE_PATTERNS = [
    r"\b(?:kill|killing)\s+(?:my\s*self|myself)\b",
    r"\b(?:end|ending)\s+(?:my\s*life|it\s*all)\b",
    r"\b(?:want|wish)\s+to\s+die\b",
    r"\b(?:commit|committing)\s+suicide\b",
    r"\bbetter\s+off\s+dead\b",
    r"\bno\s+(?:reason|point)\s+(?:to|in)\s+liv(?:e|ing)\b",
    r"\bcan(?:'t|\s+not)\s+go\s+on\s+living\b",
    r"\btake\s+my\s+(?:own\s+)?life\b",
    r"\b(?:hang|hanging)\s+myself\b",
    r"\boverdose\s+on\s+(?:pills|meds|drugs)\b",
    r"\bslit\s+(?:my\s+)?wrists?\b",
    r"\bjump\s+off\s+(?:a\s+)?(?:bridge|roof|building)\b",
    r"\b(?:wrote|written|writing)\s+(?:a\s+)?(?:suicide|goodbye)\s+note\b",
    r"\bsay(?:ing)?\s+goodbye\s+(?:to\s+everyone|forever)\b",
    r"\bdon(?:'t|\s+not)\s+want\s+to\s+wake\s+up\b",
    r"\bwish\s+I\s+(?:was|were)\s+dead\b",
]

SELF_HARM_PATTERNS = [
    r"\b(?:cut|cutting)\s+myself\b",
    r"\b(?:burn|burning)\s+myself\b",
    r"\b(?:hurt|hurting|harm|harming)\s+myself\b",
    r"\bself[\s\-_]*harm\b",
    r"\bpunish\s+my\s+(?:body|self)\b",
    r"\bmake\s+myself\s+bleed\b",
]

ACUTE_DESPAIR_PATTERNS = [
    r"\beveryone\s+would\s+be\s+better\s+(?:off\s+)?without\s+me\b",
    r"\bthere\s+is\s+no\s+(?:way\s+out|hope\s+for\s+me)\b",
    r"\bcompletely\s+hopeless\b",
    r"\bcan(?:'t|\s+not)\s+take\s+this\s+(?:pain|life)\s+any\s*more\b",
    r"\bnothing\s+will\s+ever\s+get\s+better\b",
]

# Non-crisis colloquial expressions (false positive suppression)
BENIGN_EXCLUSION_PATTERNS = [
    r"\b(?:dying|killed\s+me)\s+(?:of|from)\s+laughter\b",
    r"\b(?:dying|killed)\s+to\s+see\b",
    r"\bwould\s+kill\s+for\s+(?:a|some)\b",
    r"\bthis\s+(?:deadline|job|homework|workout|bug)\s+is\s+killing\s+me\b",
    r"\bdon(?:'t|\s+not)\s+want\s+to\s+die\b",
    r"\bafraid\s+to\s+die\b",
    r"\bfear\s+of\s+dying\b",
]


class CrisisService:
    """
    Central safety service monitoring text streams and psychological metrics for crisis signals.
    Enforces a strict non-negotiable safety circuit breaker across the platform.
    """

    @classmethod
    def evaluate(cls, text: Optional[str], user_id: Optional[Any] = None, db: Optional[Any] = None) -> Dict[str, Any]:
        """
        Evaluate text input and optional user context for crisis indicators.
        Returns safety assessment, classification severity, and immediate intervention payload.
        """
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "is_crisis": False,
                "severity": "none",
                "triggers": [],
                "response": None
            }

        cleaned = text.strip()
        lower = cleaned.lower()

        # Mask out benign idioms to avoid false positives on everyday figures of speech
        eval_text = lower
        for benign_pat in BENIGN_EXCLUSION_PATTERNS:
            eval_text = re.sub(benign_pat, " ", eval_text)

        matched_explicit = [pat for pat in EXPLICIT_SUICIDE_PATTERNS if re.search(pat, eval_text)]
        matched_self_harm = [pat for pat in SELF_HARM_PATTERNS if re.search(pat, eval_text)]
        matched_despair = [pat for pat in ACUTE_DESPAIR_PATTERNS if re.search(pat, eval_text)]

        is_crisis = False
        severity = "none"
        triggers = []

        if matched_explicit:
            is_crisis = True
            severity = "critical"
            triggers.append("suicidal_ideation")

        if matched_self_harm:
            is_crisis = True
            if severity != "critical":
                severity = "high"
            triggers.append("self_harm")

        if matched_despair and not is_crisis:
            # Despair alone is flagged as elevated concern
            severity = "elevated"
            triggers.append("acute_hopelessness")

        if is_crisis:
            return {
                "is_crisis": True,
                "severity": severity,
                "triggers": triggers,
                "response": cls.generate_crisis_response(severity=severity)
            }

        return {
            "is_crisis": False,
            "severity": severity,
            "triggers": triggers,
            "response": None
        }

    @classmethod
    def generate_crisis_response(cls, severity: str = "critical") -> Dict[str, Any]:
        """
        Generates clinical standard de-escalation message and crisis resource payload.
        """
        return {
            "title": "Immediate Support & Safety Resources",
            "message": (
                "It sounds like you are going through an overwhelming amount of pain right now. "
                "Please know you do not have to carry this alone. There are compassionate, "
                "trained people available 24/7 who want to listen and help you through this moment safely."
            ),
            "action": "crisis_helpline_intervention",
            "disclaimer": (
                "Psych-AI is an automated cognitive tool and is NOT a substitute for professional mental healthcare, "
                "medical treatment, or emergency response."
            ),
            "immediate_steps": [
                "Reach out to one of the free, confidential 24/7 crisis lines listed below immediately.",
                "If you are in immediate danger of hurting yourself, please call 911 (or your local emergency number) or go to the nearest emergency room.",
                "Reach out to a trusted family member, friend, therapist, or doctor and let them know how you are feeling.",
                "Stay in a safe environment and step away from anything you could use to harm yourself."
            ],
            "helplines": CRISIS_HELPLINES,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
