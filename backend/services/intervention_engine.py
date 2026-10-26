import random
from datetime import datetime
from sqlalchemy.orm import Session
from models.personalization import UserPolicy, PendingReward
from services.learning_engine import get_bucket, compute_state

AVAILABLE_NUDGES = {
    "stressed": ["take_break", "deep_breathing", "reframe_thought"],
    "fatigued": ["drink_water", "stand_up", "light_stretch"],
    "motivated": ["deep_work", "set_stretch_goal"],
    "calm": ["maintain_focus", "review_plan"]
}

NUDGE_TEXTS = {
    "take_break": "Step away for 5 minutes.",
    "deep_breathing": "Try 3 cycles of box breathing.",
    "reframe_thought": "Challenge your current assumption.",
    "drink_water": "Hydrate and look away from screen.",
    "stand_up": "Stand up and walk around.",
    "light_stretch": "Do a quick 2-minute stretch.",
    "deep_work": "Block out distractions right now.",
    "set_stretch_goal": "Push for one more milestone.",
    "maintain_focus": "Stay in this flow state.",
    "review_plan": "Double check upcoming priorities."
}

def get_fallback_nudge(emotion):
    nudges = AVAILABLE_NUDGES.get(emotion, ["stay_mindful"])
    return random.choice(nudges)

def select_nudge(db: Session, user_id: str, emotion: str, intensity: float, context: str = "general"):
    state_key = compute_state(context, emotion, intensity)
    
    policies = db.query(UserPolicy).filter_by(user_id=user_id, state=state_key).all()
    
    action = ""
    q_score = 0.0
    visits = 0

    if random.random() < 0.2 or not policies:
        action = get_fallback_nudge(emotion)
        pol = next((p for p in policies if p.action == action), None)
        if pol:
            days_since = (datetime.utcnow() - pol.updated_at).days if getattr(pol, 'updated_at', None) else 0
            q_score = pol.q_score * (0.98 ** days_since)
            visits = pol.visits
    else:
        # Exploit max Q applying decay
        def get_decayed_q(p):
            days_since = (datetime.utcnow() - p.updated_at).days if getattr(p, 'updated_at', None) else 0
            return p.q_score * (0.98 ** days_since)
            
        best_policy = max(policies, key=get_decayed_q)
        action = best_policy.action
        q_score = get_decayed_q(best_policy)
        visits = best_policy.visits

    pending = PendingReward(user_id=user_id, state=state_key, action=action, intensity_before=intensity)
    db.add(pending)
    db.commit()

    confidence = min(1.0, visits / 10.0) if visits >= 3 else 0.0

    return {
        "action": action,
        "text": NUDGE_TEXTS.get(action, "Take a moment to reflect."),
        "q_score": round(q_score, 2),
        "visits": visits,
        "confidence": round(confidence, 2),
        "state_key": state_key
    }
