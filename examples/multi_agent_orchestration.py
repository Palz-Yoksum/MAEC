import json
from maec import (
    start_run,
    record_received,
    record_decision,
    record_completion,
    rate_execution
)

# -------------------------------------------------
# Root orchestrator (BMAD-style)
# -------------------------------------------------

root_run = start_run(
    run_id="run_bmad_001",
    agent_id="BMAD_ORCHESTRATOR"
)

record_received(
    root_run,
    1,
    "Build a SaaS landing page"
)

record_decision(
    root_run,
    2,
    decision="DELEGATE",
    reason="Multiple specialized tasks required"
)

# -------------------------------------------------
# Product Agent
# -------------------------------------------------

product_run = start_run(
    run_id="run_product_001",
    agent_id="PRODUCT_AGENT",
    parent_run_id="run_bmad_001",
    invoked_by_agent="BMAD_ORCHESTRATOR"
)

record_received(
    product_run,
    1,
    "Define product requirements"
)

record_completion(
    product_run,
    2,
    "PRD drafted"
)

# -------------------------------------------------
# UX Agent
# -------------------------------------------------

ux_run = start_run(
    run_id="run_ux_001",
    agent_id="UX_AGENT",
    parent_run_id="run_bmad_001",
    invoked_by_agent="BMAD_ORCHESTRATOR"
)

record_received(
    ux_run,
    1,
    "Design landing page UX"
)

record_decision(
    ux_run,
    2,
    decision="ESCALATE",
    confidence=0.4,
    reason="Design direction unclear"
)

record_completion(
    ux_run,
    3,
    "Needs human review"
)

# -------------------------------------------------
# Tech Agent
# -------------------------------------------------

tech_run = start_run(
    run_id="run_tech_001",
    agent_id="TECH_AGENT",
    parent_run_id="run_bmad_001",
    invoked_by_agent="BMAD_ORCHESTRATOR"
)

record_received(
    tech_run,
    1,
    "Recommend tech stack"
)

record_completion(
    tech_run,
    2,
    "Next.js + Tailwind recommended"
)

# -------------------------------------------------
# Post-execution analysis
# -------------------------------------------------

runs = {
    "orchestrator": root_run,
    "product": product_run,
    "ux": ux_run,
    "tech": tech_run
}

print("\n--- EXECUTION RISKS ---")
for name, run in runs.items():
    print(name.upper(), "→", rate_execution(run))

with open("multi_agent_runs.json", "w") as f:
    json.dump(runs, f, indent=2)
