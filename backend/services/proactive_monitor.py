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
    def _local_now(tz_offset_minutes: int = None) -> datetime:
        from datetime import timedelta, timezone
        utc_now = datetime.now(timezone.utc)
        if tz_offset_minutes is not None:
            # JS Date.getTimezoneOffset() returns (UTC - local) in minutes
            clamped = max(-840, min(840, int(tz_offset_minutes)))
            return utc_now - timedelta(minutes=clamped)
        return utc_now

    @staticmethod
    def get_circadian_phase(hour: int = None, tz_offset_minutes: int = None) -> str:
        if hour is None:
            hour = ProactiveMonitor._local_now(tz_offset_minutes).hour
        
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
    def _alert_exists_recently(db: Session, uid_str: str, alert_type: str, hours: int = 4) -> bool:
        from datetime import timedelta, timezone
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)
        existing = (
            db.query(ProactiveAlert)
            .filter(
                ProactiveAlert.user_id == uid_str,
                ProactiveAlert.alert_type == alert_type,
                ProactiveAlert.is_acknowledged == False,
                ProactiveAlert.created_at >= cutoff,
            )
            .first()
        )
        return existing is not None

    @staticmethod
    def run_ambient_scan(db: Session, user_id: Any, tz_offset_minutes: int = None) -> Dict[str, Any]:
        local_now = ProactiveMonitor._local_now(tz_offset_minutes)
        now = local_now.replace(tzinfo=None)
        uid_str = str(user_id)
        phase = ProactiveMonitor.get_circadian_phase(local_now.hour, tz_offset_minutes)
        circadian_info = CIRCADIAN_DESCRIPTIONS.get(phase, CIRCADIAN_DESCRIPTIONS["morning_focus"])

        # 1. Fetch recent moods (last 6 entries) to measure velocity
        recent_moods = db.query(MoodLog).filter_by(user_id=uid_str).order_by(MoodLog.timestamp.desc()).limit(6).all()
        
        alerts_generated = []

        # 2. Check Stress Velocity
        if len(recent_moods) >= 3:
            recent_stress_count = sum(1 for m in recent_moods[:3] if m.mood_type in ["stressed", "fatigued"])
            if recent_stress_count >= 2:
                intensity_trend = recent_moods[0].intensity - recent_moods[2].intensity
                if (intensity_trend > 0.15 or recent_moods[0].intensity > 0.75) and not ProactiveMonitor._alert_exists_recently(db, uid_str, "burnout_velocity"):
                    alert = ProactiveAlert(
                        user_id=uid_str,
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
        if phase == "late_night_vulnerability" and not ProactiveMonitor._alert_exists_recently(db, uid_str, "circadian_friction"):
            alert = ProactiveAlert(
                user_id=uid_str,
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
        triggers = db.query(Trigger).filter_by(user_id=uid_str).all()
        if triggers and phase in ["afternoon_dip", "late_night_vulnerability"]:
            top_trigger = max(triggers, key=lambda t: t.frequency) if triggers else None
            if top_trigger and top_trigger.confidence > 0.6 and not ProactiveMonitor._alert_exists_recently(db, uid_str, "preemptive_nudge"):
                alert = ProactiveAlert(
                    user_id=uid_str,
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
            user_id=uid_str,
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
