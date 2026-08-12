#!/usr/bin/env python3
"""Flagship polyglot AI mission pipeline (portable core)."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Mission:
    mission_id: str
    objective: str
    constraints: dict[str, str] = field(default_factory=dict)
    required_capabilities: list[str] = field(default_factory=list)


@dataclass
class Plan:
    steps: list[str]
    score: float
    notes: str


@dataclass
class AuthorityDecision:
    allow: bool
    reason: str
    digest: str


@dataclass
class Receipt:
    receipt_id: str
    mission_id: str
    allow: bool
    plan_score: float
    evidence: dict[str, Any]
    content_digest: str
    sealed_unix_ms: int


def plan_mission(m: Mission) -> Plan:
    steps = ["ingress", "plan", "govern", "telemetry", "persist", "sandbox_check"]
    score = 0.82 if "evaluation" in m.required_capabilities else 0.7
    return Plan(steps=steps, score=score, notes="portable planner")


def govern(m: Mission, plan: Plan) -> AuthorityDecision:
    # Fail-closed style checks
    if plan.score < 0.5:
        return AuthorityDecision(False, "plan score below threshold", "low-score")
    if m.constraints.get("max_risk", "low") == "high" and plan.score < 0.9:
        return AuthorityDecision(False, "high risk requires higher score", "risk-gate")
    payload = f"{m.mission_id}|{plan.score}|{','.join(plan.steps)}"
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return AuthorityDecision(True, "policy satisfied", digest)


def emit_telemetry(m: Mission, decision: AuthorityDecision) -> dict[str, Any]:
    return {
        "event": "authority_decision",
        "mission_id": m.mission_id,
        "allow": decision.allow,
        "reason": decision.reason,
        "governor_digest": decision.digest,
        "ts": int(time.time() * 1000),
    }


def seal_receipt(m: Mission, plan: Plan, decision: AuthorityDecision, telemetry: dict) -> Receipt:
    evidence = {
        "plan_steps": plan.steps,
        "plan_score": plan.score,
        "telemetry": telemetry,
        "governor_digest": decision.digest,
    }
    raw = json.dumps(evidence, sort_keys=True)
    content_digest = hashlib.sha256(raw.encode()).hexdigest()[:24]
    receipt_id = hashlib.sha256(f"{m.mission_id}|{content_digest}".encode()).hexdigest()[:16]
    return Receipt(
        receipt_id=receipt_id,
        mission_id=m.mission_id,
        allow=decision.allow,
        plan_score=plan.score,
        evidence=evidence,
        content_digest=content_digest,
        sealed_unix_ms=int(time.time() * 1000),
    )


def main() -> None:
    mission = Mission(
        mission_id="demo-001",
        objective="Safe multi-agent research assist with evaluation",
        constraints={"max_risk": "low", "latency_ms": "2000"},
        required_capabilities=["evaluation", "sandbox", "receipts"],
    )
    plan = plan_mission(mission)
    decision = govern(mission, plan)
    telemetry = emit_telemetry(mission, decision)
    receipt = seal_receipt(mission, plan, decision, telemetry)

    out = {
        "mission": asdict(mission),
        "plan": asdict(plan),
        "decision": asdict(decision),
        "receipt": asdict(receipt),
    }
    print(json.dumps(out, indent=2))
    assert receipt.allow, "expected allow for demo mission"
    print("\nflagship pipeline: ok")
    print(f"receipt_id={receipt.receipt_id} digest={receipt.content_digest}")


if __name__ == "__main__":
    main()
