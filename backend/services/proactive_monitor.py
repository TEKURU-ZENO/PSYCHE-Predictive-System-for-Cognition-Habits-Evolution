from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models.proactive import ProactiveAlert
from models.mood import MoodLog
from models.pattern import Trigger
from models.user_state import UserState

CIRCADIAN_DESCRIPTIONS = {
    "morning_focus": {
        "title": "Morning Focus Phase",
        "description": "High executive clarity and cognitive reserve. Optimal for high-complexity problem solving.",
        "mode": "execution"
    },
    "midday_surge": {
        "title": "Midday Execution Surge",
        "description": "Peak task momentum. Ensure hydration and periodic 2-minute resets to avoid mid-afternoon burnout.",
        "mode": "momentum"
    },
    "afternoon_dip": {
        "title": "Afternoon Cognitive Dip",
        "description": "Natural circadian dip in dopamine & executive attention. Vulnerability to frustration and cognitive distortions is elevated.",
        "mode": "conservation"
    },
    "evening_wind_down": {
        "title": "Evening Integration Phase",
        "description": "Shift from execution to reflective integration. Ideal for journaling, retrospective review, and low-cognitive-load winding down.",
        "mode": "reflection"
    },
    "late_night_vulnerability": {
        "title": "Late-Night Vulnerability Window",
        "description": "Prefrontal cortex regulation is depleted. Critical risk of catastrophizing, rumination, and imposter spirals.",
        "mode": "grounding"
    }
}

class ProactiveMonitor:
    @staticmethod
    def get_circadian_phase(hour: int = None) -> str:
        if hour is None:
            hour = datetime.utcnow().hour  # Note: Can be localized
        
        if 6 <= hour < 11:
            return "morning_focus"
        elif 11 <= hour < 14:
            return "midday_surge"
        elif 14 <= hour < 17:
            return "afternoon_dip"
        elif 17 <= hour < 22:
            return "evening_wind_down"
        else:
            return "late_night_vulnerability"

    @staticmethod
    def run_ambient_scan(db: Session, user_id: int) -> Dict[str, Any]:
        now = datetime.utcnow()
        phase = ProactiveMonitor.get_circadian_phase(now.hour)
        circadian_info = CIRCADIAN_DESCRIPTIONS.get(phase, CIRCADIAN_DESCRIPTIONS["morning_focus"])

        # 1. Fetch recent moods (last 6 entries) to measure velocity
        recent_moods = db.query(MoodLog).filter_by(user_id=str(user_id)).order_by(MoodLog.timestamp.desc()).limit(6).all()
        
        alerts_generated = []

        # 2. Check Stress Velocity
        if len(recent_moods) >= 3:
            recent_stress_count = sum(1 for m in recent_moods[:3] if m.mood_type in ["stressed", "fatigued"])
            if recent_stress_count >= 2:
                intensity_trend = recent_moods[0].intensity - recent_moods[2].intensity
                if intensity_trend > 0.15 or recent_moods[0].intensity > 0.75:
                    alert = ProactiveAlert(
                        user_id=user_id,
                        alert_type="burnout_velocity",
                        severity="critical" if recent_moods[0].intensity > 0.8 else "moderate",
                        title="Accelerated Stress Velocity Detected",
                        message=f"Negative emotional velocity is climbing (+{round(intensity_trend * 100)}% over last logs). Cognitive twin recommends a forced micro-reset before decision capacity degrades.",
                        preemptive_action="box_breathing",
                        circadian_phase=phase,
                        is_acknowledged=False,
                        created_at=now
                    )
                    db.add(alert)
                    alerts_generated.append(alert)

        # 3. Circadian Vulnerability Warning (Late Night)
        if phase == "late_night_vulnerability":
            alert = ProactiveAlert(
                user_id=user_id,
                alert_type="circadian_friction",
                severity="moderate",
                title="Late-Night Cognitive Exhaustion Risk",
                message="Operating during circadian depletion window. Analytical reasoning tends toward all-or-nothing framing at this hour. Delay critical decisions until morning focus phase.",
                preemptive_action="socratic_pause",
                circadian_phase=phase,
                is_acknowledged=False,
                created_at=now
            )
            db.add(alert)
            alerts_generated.append(alert)

        # 4. Preemptive Trigger Prevention
        triggers = db.query(Trigger).filter_by(user_id=str(user_id)).all()
        if triggers and phase in ["afternoon_dip", "late_night_vulnerability"]:
            top_trigger = max(triggers, key=lambda t: t.frequency) if triggers else None
            if top_trigger and top_trigger.confidence > 0.6:
                alert = ProactiveAlert(
                    user_id=user_id,
                    alert_type="preemptive_nudge",
                    severity="low",
                    title=f"Preemptive Safeguard: {top_trigger.event.capitalize()} Sensitivity",
                    message=f"You historically show an elevated risk of {top_trigger.emotion} state during {top_trigger.event} in the {phase.replace('_', ' ')}. Consider preemptively chunking your workload.",
                    preemptive_action="task_chunking",
                    circadian_phase=phase,
                    is_acknowledged=False,
                    created_at=now
                )
                db.add(alert)
                alerts_generated.append(alert)

        db.commit()

        # Fetch active unacknowledged alerts for this user
        active_alerts = db.query(ProactiveAlert).filter_by(
            user_id=user_id,
            is_acknowledged=False
        ).order_by(ProactiveAlert.created_at.desc()).limit(5).all()

        return {
            "status": "active",
            "circadian_phase": phase,
            "circadian_info": circadian_info,
            "active_alerts": [
                {
                    "id": a.id,
                    "type": a.alert_type,
                    "severity": a.severity,
                    "title": a.title,
                    "message": a.message,
                    "preemptive_action": a.preemptive_action,
                    "circadian_phase": a.circadian_phase,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in active_alerts
            ],
            "last_scan": now.isoformat()
        }
