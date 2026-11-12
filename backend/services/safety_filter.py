import re

_DIAGNOSTIC_PATTERNS = [
    re.compile(r"\byou\s+(?:definitely\s+)?have\s+(?:a\s+)?(?:clinical\s+)?(?:disorder|depression|adhd|bipolar|ptsd)\b", re.IGNORECASE),
    re.compile(r"\bclinical\s+diagnosis\b", re.IGNORECASE),
    re.compile(r"\bdiagnosed\s+with\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+definitely\b", re.IGNORECASE),
]


def sanitize(output: dict, confidence: float):
    text = str(output.get("text", ""))

    for pat in _DIAGNOSTIC_PATTERNS:
        text = pat.sub("you may be experiencing patterns associated with", text)

    # Remove standalone forbidden diagnostic terms case-insensitively on word boundaries
    text = re.sub(r"\b(?:diagnosis|disorder)\b", "pattern", text, flags=re.IGNORECASE)

    if confidence < 0.6 and "may" not in text.lower() and "could" not in text.lower():
        text = re.sub(r"\byou are\b", "you may be", text, flags=re.IGNORECASE)
        text = re.sub(r"\bthis is\b", "this could be", text, flags=re.IGNORECASE)

    output["text"] = text
    return output
