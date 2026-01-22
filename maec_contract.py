# maec_contract.py

# -------------------------------
# State-specific MAEC rules
# -------------------------------
STATE_RULES = {
    "RECEIVED": {
        "required": ["input"],
        "forbidden": ["decision", "outcome"]
    },
    "DECIDING": {
        "required": ["decision"],
        "forbidden": ["outcome"]
    },
    "COMPLETED": {
        "required": ["outcome"],
        "forbidden": ["decision"]
    }
}


def create_execution_run(
    run_id,
    agent_id,
    parent_run_id=None,
    invoked_by_agent=None
):
    """
    Creates a new execution run.
    Supports parent-child relationships for multi-agent systems.
    """
    return {
        "run_id": run_id,
        "agent_id": agent_id,
        "parent_run_id": parent_run_id,
        "invoked_by_agent": invoked_by_agent,
        "events": []
    }



def validate_event(event):
    """
    Enforces MAEC rules for a single event.
    """

    # Fields required for ALL events
    base_required = ["step_id", "state", "timestamp"]
    for field in base_required:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")

    state = event["state"]

    # Enforce state-specific rules
    rules = STATE_RULES.get(state)
    if rules:
        for field in rules.get("required", []):
            if field not in event:
                raise ValueError(
                    f"{state} event missing required field: {field}"
                )

        for field in rules.get("forbidden", []):
            if field in event:
                raise ValueError(
                    f"{state} event must not include field: {field}"
                )


def add_event(execution_run, event):
    """
    Adds an event only if it passes MAEC validation.
    """
    validate_event(event)
    execution_run["events"].append(event)


def rate_execution(execution_run):
    """
    Produces a simple risk rating for an execution run.
    Returns: LOW, MEDIUM, or HIGH
    """

    events = execution_run.get("events", [])

    decision_event = None
    completion_event = None

    for event in events:
        if event["state"] == "DECIDING":
            decision_event = event
        if event["state"] == "COMPLETED":
            completion_event = event

    # If no completion, treat as high risk
    if not completion_event:
        return "HIGH"

    # Escalation is always high risk
    if decision_event and decision_event.get("decision") == "ESCALATE":
        return "HIGH"

    # Confidence-based assessment
    confidence = decision_event.get("confidence") if decision_event else None

    if confidence is None:
        return "MEDIUM"

    if confidence >= 0.7:
        return "LOW"

    return "MEDIUM"

from datetime import datetime


def _now():
    return datetime.utcnow().isoformat()


# -------------------------------
# Public MAEC API (Day 8)
# -------------------------------

def start_run(run_id, agent_id, parent_run_id=None, invoked_by_agent=None):
    return create_execution_run(
        run_id=run_id,
        agent_id=agent_id,
        parent_run_id=parent_run_id,
        invoked_by_agent=invoked_by_agent
    )


def record_received(execution_run, step_id, input_data):
    add_event(execution_run, {
        "step_id": step_id,
        "state": "RECEIVED",
        "input": input_data,
        "timestamp": _now()
    })


def record_decision(
    execution_run,
    step_id,
    decision,
    confidence=None,
    reason=None
):
    event = {
        "step_id": step_id,
        "state": "DECIDING",
        "decision": decision,
        "timestamp": _now()
    }

    if confidence is not None:
        event["confidence"] = confidence
    if reason is not None:
        event["reason"] = reason

    add_event(execution_run, event)


def record_completion(execution_run, step_id, outcome):
    add_event(execution_run, {
        "step_id": step_id,
        "state": "COMPLETED",
        "outcome": outcome,
        "timestamp": _now()
    })


def get_risk_rating(execution_run):
    return rate_execution(execution_run)
