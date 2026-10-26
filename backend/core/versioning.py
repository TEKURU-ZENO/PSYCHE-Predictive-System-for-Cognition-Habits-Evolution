import hashlib
import json
from typing import Dict, Any

class SystemVersionController:
    # Phase 10.4: Unified System Version Registry
    VERSION_REGISTRY = {
        "core": "v1.7.0",
        "agents": "v2.4.0",
        "debate": "v1.5.0",
        "learning": "v2.1.0",
        "guardrails": "v1.2.0",
        "memory": "v1.1.0",
        "proactive": "v1.0.0",
        "red_team": "v1.0.0",
        "post_mortem": "v1.0.0",
        "replay": "v1.0.0",
        "streaming": "v1.0.0",
        "vault": "v1.0.0"
    }
    
    COMPATIBILITY_MATRIX = {
        "agents": {"v2.1.0": ["v2.0.0", "v2.1.0"]},
        "learning": {"v2.0.1": ["v2.0.0", "v2.0.1"]},
    }

    @staticmethod
    def get_version_matrix() -> Dict[str, str]:
        """Returns the centralized immutable version registry."""
        return dict(SystemVersionController.VERSION_REGISTRY)

    @staticmethod
    def generate_decision_hash(decision_payload: Dict[str, Any]) -> str:
        """
        Generates a forensic-grade SHA256 hash of a major decision to ensure replayability
        and trace integrity.
        """
        # Ensure we always include the current version matrix in the hash
        payload_with_versions = {
            **decision_payload,
            "system_versions": SystemVersionController.VERSION_REGISTRY
        }
        
        # Sort keys to ensure deterministic hashing
        serialized = json.dumps(payload_with_versions, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        
    @staticmethod
    def get_compatibility_flags(agent_versions_used: Dict[str, str]) -> bool:
        """
        Check if we are running in a backward compatibility mode for older logs.
        """
        # Simplistic check for Phase 10
        return False
