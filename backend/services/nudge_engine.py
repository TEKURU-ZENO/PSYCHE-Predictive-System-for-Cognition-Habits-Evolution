def generate_nudge(mood_type: str, intensity: float):
    if mood_type == "stressed" and intensity > 0.7:
        return {
            "type": "break",
            "message": "You seem stressed. Take a 5-minute reset."
        }
    elif mood_type == "fatigued":
        return {
            "type": "energy",
            "message": "Low energy detected. Try a short walk or hydration."
        }
    elif mood_type == "motivated":
        return {
            "type": "action",
            "message": "You're in a good state—start something meaningful now."
        }
    return None
