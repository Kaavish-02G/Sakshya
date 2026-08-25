from datetime import datetime


def audit_custody(events: list[dict], max_gap_hours: int = 8) -> dict:
    """Apply transparent rules; no LLM inference is used to invent anomalies."""
    if not events:
        return {"gap_detected": True, "severity": "HIGH", "explanation": "No custody events are recorded."}
    for event in events:
        if not event.get("custodian") or not event.get("action") or not event.get("hash"):
            return {"gap_detected": True, "severity": "HIGH", "explanation": "A custody event is missing custodian, action, or SHA-256 hash."}
    ordered = sorted(events, key=lambda event: event["timestamp"])
    for earlier, later in zip(ordered, ordered[1:]):
        hours = (datetime.fromisoformat(later["timestamp"]) - datetime.fromisoformat(earlier["timestamp"])).total_seconds() / 3600
        if hours > max_gap_hours:
            return {"gap_detected": True, "severity": "HIGH", "explanation": f"A {hours:.1f}-hour gap exists between custody events."}
    return {"gap_detected": False, "severity": "NONE", "explanation": "No rule-based custody gap detected."}
