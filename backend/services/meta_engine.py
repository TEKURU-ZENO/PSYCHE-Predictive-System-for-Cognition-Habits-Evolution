from sqlalchemy.orm import Session
from models.behavior import BehaviorLog
from models.mood import MoodLog
from models.pattern import Trigger
from models.personalization import UserPolicy
from models.goals import Goal
from services.prediction_engine import project_long_term_risk

def map_archetype(user_id: str, db: Session):
    T = {"Wizard": 0.5, "Warrior": 0.5, "Explorer": 0.5, "Creator": 0.5, "Caregiver": 0.5, "Rebel": 0.5, "Everyman": 0.5}
    
    behaviors = db.query(BehaviorLog).filter_by(user_id=user_id).all()
    B = {k: 0.1 for k in T.keys()}
    coding_count = sum(1 for b in behaviors if b.context == "coding")
    meeting_count = sum(1 for b in behaviors if b.context == "meeting")
    if coding_count > 0:
        B["Wizard"] += 0.4
        B["Creator"] += 0.3
    if meeting_count > 0:
        B["Explorer"] += 0.3
        B["Caregiver"] += 0.2

    policies = db.query(UserPolicy).filter(UserPolicy.user_id == user_id, UserPolicy.visits >= 3).all()
    R = {k: 0.1 for k in T.keys()}
    for p in policies:
        if p.q_score > 0.5:
            if "deep_work" in p.action: R["Warrior"] += 0.3
            if "reframe_thought" in p.action: R["Wizard"] += 0.3
            if "stand_up" in p.action: R["Explorer"] += 0.2
            
    triggers = db.query(Trigger).filter_by(user_id=user_id).all()
    Tr = {k: 0.1 for k in T.keys()}
    for t in triggers:
        if t.emotion == "stressed":
            if t.event == "coding": Tr["Wizard"] -= 0.2
            if t.event == "meeting": Tr["Explorer"] -= 0.2

    w_T, w_B, w_R, w_Tr = 0.3, 0.3, 0.25, 0.15
    
    final_scores = {}
    for k in T.keys():
        score = (w_T * T[k]) + (w_B * B[k]) + (w_R * R[k]) + (w_Tr * Tr[k])
        final_scores[k] = max(0.1, score)
        
    total = sum(final_scores.values()) or 1.0
    distributions = {k: round(v/total, 2) for k, v in final_scores.items()}
    sorted_archs = sorted(distributions.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "dominant": sorted_archs[0][0],
        "secondary": sorted_archs[1][0],
        "distribution": distributions
    }

def detect_dissonance(user_id, db: Session):
    behaviors = db.query(BehaviorLog).filter_by(user_id=user_id).all()
    triggers = db.query(Trigger).filter_by(user_id=user_id).all()
    goals = db.query(Goal).filter_by(user_id=user_id).all()
    
    coding_goals = 10 
    for g in goals:
        if "code" in g.goal.lower() or "coding" in g.goal.lower():
            coding_goals = 20 if g.priority == "high" else 10
            
    completed = sum(1 for b in behaviors if b.context == "coding")
    gap = 1 - (min(completed, coding_goals) / coding_goals)
    
    has_high_priority = any(g.priority == "high" for g in goals)
    if has_high_priority:
        gap *= 1.5
    else:
        gap *= 0.7
    
    trigger_freq = sum(t.frequency for t in triggers if t.emotion == "stressed")
    dissonance = gap * (1 + (min(trigger_freq, 5)/5.0))
    dissonance = max(0.0, min(1.0, dissonance))
    
    insight = "Behaviors align closely with structural expectations."
    if dissonance > 0.6:
        insight = "You value discipline, but tend to avoid structured tasks under stress."
        
    return {
        "gap_score": round(gap, 2),
        "dissonance": round(dissonance, 2),
        "insight": insight
    }

def generate_meta_profile(db: Session, user_id: str):
    archetype = map_archetype(user_id, db)
    dissonance = detect_dissonance(user_id, db)
    
    moods = db.query(MoodLog).filter_by(user_id=user_id).order_by(MoodLog.timestamp.asc()).all()
    triggers = db.query(Trigger).filter_by(user_id=user_id).all()
    policies = db.query(UserPolicy).filter_by(user_id=user_id).all()
    
    projection = project_long_term_risk(moods, triggers, policies)
    
    return {
        "archetype": archetype,
        "dissonance": dissonance,
        "7_day_projection": projection
    }
