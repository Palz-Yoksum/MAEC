from datetime import datetime

# --------------------------------------------------
# MAEC Core
# Responsibility:
# - Define valid execution states
# - Record agent execution events
# - Enforce execution correctness
# --------------------------------------------------

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


def _now():
    """
    Internal helper to generate timestamps.
    Kept private on purpose.
    """
    return datetime.utcnow().isoformat()


def start_run(run_id, agent_id, parent_run_id=None, invoked_by_agent=None):
    """
    Create a new MAEC execution run.

    This is the root container for all execution events.
    """
    return {
        "run_id": run_id,
        "agent_id": agent_id,
        "parent_run_id": parent_run_id,
        "invoked_by_agent": invoked_by_agent,
        "events": []
    }


def _validate_event(event):
    """
    Enforce MAEC execution contract rules.
    This is the heart of MAEC correctness.
    """
    # Base required fields
    base_required = ["step_id", "state", "timestamp"]
    for field in base_required:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")

    # State-specific rules
    rules = STATE_RULES.get(event["state"])
    if rules:
        for field in rules.get("required", []):
            if field not in event:
                raise ValueError(
                    f"{event['state']} state missing required field: {field}"
                )

        for field in rules.get("forbidden", []):
            if field in event:
                raise ValueError(
                    f"{event['state']} state must not include field: {field}"
                )


def _add_event(run, event):
    """
    Internal helper to add a validated event to a run.
    """
    _validate_event(event)
    run["events"].append(event)


def record_received(run, step_id, input_data):
    """
    Record that the agent received input.
    """
    _add_event(run, {
        "step_id": step_id,
        "state": "RECEIVED",
        "input": input_data,
        "timestamp": _now()
    })


def record_decision(run, step_id, decision, confidence=None, reason=None):
    """
    Record a decision made by the agent.
    """
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

    _add_event(run, event)


def record_completion(run, step_id, outcome):
    """
    Record execution completion.
    """
    _add_event(run, {
        "step_id": step_id,
        "state": "COMPLETED",
        "outcome": outcome,
        "timestamp": _now()
    })
