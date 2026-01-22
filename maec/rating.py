# --------------------------------------------------
# MAEC Rating
# Responsibility:
# - Interpret execution behavior
# - Assign a trust / risk level
# --------------------------------------------------

def rate_execution(run):
    """
    Assign a risk level to an execution run.

    Returns:
        "LOW", "MEDIUM", or "HIGH"
    """

    decision_event = None
    completed = False

    for event in run.get("events", []):
        if event["state"] == "DECIDING":
            decision_event = event
        elif event["state"] == "COMPLETED":
            completed = True

    # Rule 1: If execution never completed → HIGH risk
    if not completed:
        return "HIGH"

    # Rule 2: Explicit escalation → HIGH risk
    if decision_event and decision_event.get("decision") == "ESCALATE":
        return "HIGH"

    # Rule 3: Confidence-based interpretation
    confidence = decision_event.get("confidence") if decision_event else None

    if confidence is None:
        return "MEDIUM"

    if confidence >= 0.7:
        return "LOW"

    return "MEDIUM"
