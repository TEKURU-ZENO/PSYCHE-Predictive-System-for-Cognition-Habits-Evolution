def build_context(user_state, signals, basis, constraints=None):
    return {
        "state": user_state,             
        "signals": signals,              
        "basis": basis,                  
        "constraints": constraints or {
            "tone": "non-judgmental",
            "no_diagnosis": True
        }
    }
