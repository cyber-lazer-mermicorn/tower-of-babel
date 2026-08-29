"""Megamind — Autonomous Build Foundry Director.

Runs as: python -m tower megamind [--project PATH] [--wave N] [--dry-run]

The Mastermind/Megamind pattern:
  MASTERMIND  = continuous builder and integrator (runs every wave)
  MEGAMIND    = periodic whole-system challenger (runs at wave boundaries)

This module implements both roles as a structured, registry-aware
build loop that any autonomous coding agent (Kilo Code, Claude, etc.)
can execute against any Tower-registered project.
"""

from __future__ import annotations

import json
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

WaveNumber = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

Priority = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "OPPORTUNITY"]


@dataclass
class Finding:
    priority: Priority
    specialist: str
    description: str
    file_hint: str = ""

    def to_dict(self) -> dict:
        return {
            "priority": self.priority,
            "specialist": self.specialist,
            "description": self.description,
            "file_hint": self.file_hint,
        }


@dataclass
class WaveResult:
    wave: int
    wave_name: str
    findings: list[Finding] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    verified: bool = False
    blockers: list[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.priority == "CRITICAL")

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.priority == "HIGH")

    def to_dict(self) -> dict:
        return {
            "wave": self.wave,
            "wave_name": self.wave_name,
            "verified": self.verified,
            "critical": self.critical_count,
            "high": self.high_count,
            "findings": [f.to_dict() for f in self.findings],
            "actions_taken": self.actions_taken,
            "blockers": self.blockers,
        }


# ---------------------------------------------------------------------------
# Wave definitions
# ---------------------------------------------------------------------------

WAVE_DEFINITIONS: dict[int, dict] = {
    0: {
        "name": "Reconnaissance",
        "objective": "Read the full repository. Build an internal map. Identify what works, what is incomplete, what is broken, what is redundant, what is missing.",
        "entry_criteria": "Any project state.",
        "exit_criteria": "Architecture map produced. High-value findings ranked.",
        "specialists": ["architect", "quality"],
        "questions": [
            "What exists and works today?",
            "What is incomplete but structurally sound?",
            "What is broken or silently failing?",
            "What is duplicated or redundant?",
            "What is entirely missing?",
            "What is unusually strong and must be preserved?",
        ],
    },
    1: {
        "name": "Make It Run",
        "objective": "Get the complete system runnable. Backend starts, frontend starts, database initializes, migrations execute, core workflow executes.",
        "entry_criteria": "Wave 0 complete.",
        "exit_criteria": "System runs end-to-end without crashing on the happy path.",
        "specialists": ["architect", "backend", "platform", "data"],
        "checklist": [
            "backend starts without errors",
            "frontend starts without errors",
            "database initializes",
            "migrations execute",
            "services connect",
            "configuration resolves",
            "core workflow executes",
        ],
    },
    2: {
        "name": "Complete Core Loop",
        "objective": "Make the defining user workflow complete. All major components participate correctly.",
        "entry_criteria": "System runs (Wave 1 complete).",
        "exit_criteria": "User input → validation → processing → persistence → result → user feedback all work.",
        "specialists": ["backend", "frontend", "data", "ux"],
        "checklist": [
            "input validation works",
            "processing produces correct output",
            "persistence is durable",
            "result is surfaced to user",
            "errors are actionable",
        ],
    },
    3: {
        "name": "Harden",
        "objective": "Add validation, timeouts, retries, error recovery, permissions, security, transaction correctness, idempotency, resource limits. Test failure paths.",
        "entry_criteria": "Core loop complete (Wave 2).",
        "exit_criteria": "System survives common failure modes without silent corruption.",
        "specialists": ["security", "backend", "data", "test", "recovery"],
        "checklist": [
            "input validation on all routes",
            "auth checked before every mutation",
            "retries with backoff on external calls",
            "idempotency on consequential operations",
            "transaction boundaries correct",
            "resource limits enforced",
            "failure paths tested",
        ],
    },
    4: {
        "name": "Professionalize",
        "objective": "Improve UX, accessibility, API ergonomics, developer experience, logging, documentation, maintainability. Remove prototype artifacts.",
        "entry_criteria": "System is hardened (Wave 3).",
        "exit_criteria": "System is operable by a new team member without tribal knowledge.",
        "specialists": ["ux", "frontend", "observability", "quality", "docs"],
        "checklist": [
            "all screens have loading/empty/error states",
            "all important operations emit structured logs",
            "README and RUNTIME.md are current",
            "no prototype placeholder copy in UI",
            "DECISIONS.md updated for non-obvious choices",
        ],
    },
    5: {
        "name": "Performance",
        "objective": "Profile the real system. Improve the largest bottlenecks. Preserve correctness.",
        "entry_criteria": "System is professional (Wave 4).",
        "exit_criteria": "Known bottlenecks addressed. Benchmarks recorded.",
        "specialists": ["performance", "data", "backend", "frontend"],
        "checklist": [
            "N+1 queries eliminated",
            "database indexes on high-read columns",
            "external API calls cached where appropriate",
            "frontend bundle size reviewed",
            "render churn minimized",
        ],
    },
    6: {
        "name": "Advanced Capability",
        "objective": "Raise the ceiling. Add real-time, semantic intelligence, automation, multi-user, or distributed capabilities.",
        "entry_criteria": "Performance optimized (Wave 5).",
        "exit_criteria": "At least one high-leverage advanced capability added and verified.",
        "specialists": ["architect", "backend", "intelligence", "platform"],
        "innovation_questions": [
            "What currently requires a human but could be automated?",
            "What information exists but is not being connected?",
            "What repeated workflow could become a pipeline?",
            "What subsystem could become self-improving?",
            "Where can A + B become A × B?",
        ],
    },
    7: {
        "name": "Polish",
        "objective": "Review the application as a product. Fix awkward flows, rough UI, confusing terminology, weak onboarding, missing affordances.",
        "entry_criteria": "Advanced capabilities added (Wave 6).",
        "exit_criteria": "System feels designed rather than accumulated.",
        "specialists": ["ux", "frontend", "quality"],
    },
    8: {
        "name": "Adversarial Review",
        "objective": "Attempt to break the system. Test invalid inputs, huge files, missing config, network failures, concurrent writes, auth bypass attempts.",
        "entry_criteria": "System is polished (Wave 7).",
        "exit_criteria": "No critical or high-severity security or reliability defects remain.",
        "specialists": ["security", "test", "recovery"],
        "attack_vectors": [
            "invalid / oversized inputs",
            "missing required configuration",
            "network failures mid-operation",
            "duplicate / concurrent requests",
            "authorization bypass attempts",
            "partial crashes and restart during processing",
            "malformed external API responses",
        ],
    },
    9: {
        "name": "Deployment Proof",
        "objective": "Build and run the actual deployment form. Validate container, config, database startup, migrations, health checks, networking, restart behavior.",
        "entry_criteria": "Adversarial review passed (Wave 8).",
        "exit_criteria": "Production deployment succeeds and is verifiably healthy.",
        "specialists": ["platform", "observability", "backend"],
        "checklist": [
            "container builds without error",
            "configuration resolves in production env",
            "database starts and migrations apply",
            "health checks pass",
            "service dependencies available",
            "persistent storage durable",
            "frontend delivered correctly",
            "graceful shutdown and restart work",
        ],
    },
    10: {
        "name": "Genius Pass",
        "objective": "Deliberate upper-level improvement. Each specialist asks: if an elite engineer owned this for another month, what would they improve? Select and implement the strongest coherent subset.",
        "entry_criteria": "System is deployed and verified (Wave 9).",
        "exit_criteria": "At least one meaningful nonlinear capability improvement shipped.",
        "specialists": ["all"],
        "megamind_questions": [
            "What is architecturally weak?",
            "What subsystem is holding back the rest?",
            "What capability is unexpectedly close to becoming possible?",
            "What complexity can be eliminated?",
            "What valuable components are not yet connected?",
            "What single redesign would produce the highest leverage?",
        ],
    },
}

# ---------------------------------------------------------------------------
# Specialist definitions
# ---------------------------------------------------------------------------

SPECIALISTS = {
    "architect": "System boundaries, domain models, data flows, dependency map, extension points",
    "backend": "Domain services, APIs, business logic, validation, jobs, concurrency, retries",
    "frontend": "App pages, components, state, forms, loading/empty/error states, accessibility",
    "data": "Schema, migrations, constraints, indexes, query design, transaction boundaries",
    "security": "Auth, authorization, RLS/ACL, secrets, input validation, injection, SSRF, audit",
    "test": "Unit, component, integration, contract, E2E, regression — consequential behavior",
    "ux": "Information architecture, flow, terminology, onboarding, feedback, accessibility",
    "performance": "Latency, N+1, indexes, caching, bundle size, render churn, async I/O",
    "observability": "Structured logging, tracing, correlation IDs, metrics, alerting",
    "platform": "CI/CD, containers, secrets, health checks, deployment, scaling",
    "quality": "Duplication, dead code, naming, coupling, complexity, refactoring",
    "recovery": "Retry, backoff, timeout, idempotency, dead-letter, partial success, replay",
    "intelligence": "Automation, semantic retrieval, agent pipelines, adaptive scheduling",
    "docs": "README, ARCHITECTURE, DECISIONS, RUNTIME, API, recovery procedures",
    "integration": "Frontend↔API↔domain↔persistence coherence, specialist change integration",
}

# ---------------------------------------------------------------------------
# Priority engine
# ---------------------------------------------------------------------------

def score_finding(impact: float, confidence: float, leverage: float, urgency: float, cost: float) -> float:
    """Score a candidate task using the Mastermind priority formula.

    score = (IMPACT × CONFIDENCE × LEVERAGE × URGENCY) / COST

    All inputs are 0.0–1.0. Higher score = do this first.
    """
    if cost <= 0:
        cost = 0.01
    return (impact * confidence * leverage * urgency) / cost


# ---------------------------------------------------------------------------
# Reconnaissance reader
# ---------------------------------------------------------------------------

def recon_project(project_path: Path) -> dict:
    """Non-destructive reconnaissance pass over a project directory.

    Reads structure and key indicator files. Does not modify anything.
    Returns a findings dict suitable for the Mastermind operating loop.
    """
    p = project_path.resolve()
    if not p.exists():
        return {"error": f"Path not found: {p}"}

    indicators: dict[str, bool] = {
        "has_agents_md": (p / "AGENTS.md").exists(),
        "has_readme": (p / "README.md").exists(),
        "has_package_json": (p / "package.json").exists(),
        "has_pyproject": (p / "pyproject.toml").exists(),
        "has_dockerfile": (p / "Dockerfile").exists() or (p / "docker-compose.yml").exists(),
        "has_ci": (p / ".github" / "workflows").exists(),
        "has_tests": any([
            (p / "tests").exists(),
            (p / "test").exists(),
            (p / "__tests__").exists(),
            (p / "spec").exists(),
        ]),
        "has_migrations": (p / "supabase" / "migrations").exists() or (p / "migrations").exists(),
        "has_env_example": (p / ".env.example").exists() or (p / ".env.example.local").exists(),
        "has_decisions": (p / "docs" / "DECISIONS.md").exists(),
        "has_runtime_doc": (p / "docs" / "RUNTIME.md").exists() or (p / "docs" / "runtime.md").exists(),
    }

    # Detect language
    languages: list[str] = []
    if (p / "package.json").exists():
        languages.append("typescript/javascript")
    if any(p.rglob("*.py")):
        languages.append("python")
    if any(p.rglob("*.go")):
        languages.append("go")
    if any(p.rglob("*.rs")):
        languages.append("rust")

    # Read key files if they exist
    agents_summary = ""
    if (p / "AGENTS.md").exists():
        text = (p / "AGENTS.md").read_text(errors="replace")
        agents_summary = text[:500] + ("..." if len(text) > 500 else "")

    # Count source files as a rough size signal
    ts_files = list(p.rglob("*.ts")) + list(p.rglob("*.tsx"))
    py_files = list(p.rglob("*.py"))
    test_files = [f for f in ts_files + py_files if "test" in f.name.lower() or "spec" in f.name.lower()]

    # Identify obvious gaps
    gaps: list[str] = []
    if not indicators["has_agents_md"]:
        gaps.append("No AGENTS.md — add Mastermind foundry instruction")
    if not indicators["has_tests"]:
        gaps.append("No test directory — zero test coverage")
    if not indicators["has_ci"]:
        gaps.append("No CI/CD workflows")
    if not indicators["has_env_example"]:
        gaps.append("No .env.example — configuration is undocumented")
    if not indicators["has_decisions"]:
        gaps.append("No DECISIONS.md — architecture choices undocumented")
    if not indicators["has_runtime_doc"]:
        gaps.append("No RUNTIME.md — local setup undocumented")
    if len(test_files) == 0 and (len(ts_files) + len(py_files)) > 10:
        gaps.append(f"0 test files found against {len(ts_files) + len(py_files)} source files")

    return {
        "path": str(p),
        "indicators": indicators,
        "languages": languages,
        "source_file_count": len(ts_files) + len(py_files),
        "test_file_count": len(test_files),
        "gaps": gaps,
        "agents_md_preview": agents_summary,
    }


# ---------------------------------------------------------------------------
# Wave planner
# ---------------------------------------------------------------------------

def plan_wave(wave: int, recon: dict) -> WaveResult:
    """Produce a structured plan for a given wave based on recon findings."""
    defn = WAVE_DEFINITIONS.get(wave)
    if not defn:
        return WaveResult(wave=wave, wave_name="Unknown", blockers=[f"Wave {wave} not defined"])

    result = WaveResult(wave=wave, wave_name=defn["name"])

    # Generate findings from recon gaps
    gap_to_priority: dict[str, Priority] = {
        "No AGENTS.md": "HIGH",
        "No test directory": "HIGH",
        "No CI/CD": "MEDIUM",
        "No .env.example": "MEDIUM",
        "No DECISIONS.md": "LOW",
        "No RUNTIME.md": "MEDIUM",
        "0 test files": "HIGH",
    }
    for gap in recon.get("gaps", []):
        priority: Priority = "MEDIUM"
        for key, p in gap_to_priority.items():
            if key in gap:
                priority = p
                break
        specialist = "quality"
        if "test" in gap.lower():
            specialist = "test"
        elif "ci" in gap.lower() or "env" in gap.lower():
            specialist = "platform"
        elif "runtime" in gap.lower() or "decisions" in gap.lower():
            specialist = "docs"
        result.findings.append(Finding(
            priority=priority,
            specialist=specialist,
            description=gap,
        ))

    # Actions this wave should perform
    checklist = defn.get("checklist", [])
    for item in checklist:
        result.actions_taken.append(f"[ ] {item}")

    return result


# ---------------------------------------------------------------------------
# Megamind challenger
# ---------------------------------------------------------------------------

def megamind_review(recon: dict) -> list[Finding]:
    """Fresh-eyes architectural challenge pass.

    Asks the Megamind questions without inheriting implementation assumptions.
    Returns prioritized findings for the Mastermind to evaluate.
    """
    findings: list[Finding] = []
    questions = WAVE_DEFINITIONS[10]["megamind_questions"]

    # Structural signals
    if recon.get("test_file_count", 0) == 0 and recon.get("source_file_count", 0) > 5:
        findings.append(Finding(
            priority="CRITICAL",
            specialist="test",
            description="Zero test coverage on a non-trivial codebase. Any refactor is flying blind.",
        ))

    if not recon["indicators"].get("has_agents_md"):
        findings.append(Finding(
            priority="HIGH",
            specialist="architect",
            description="No AGENTS.md. Autonomous agents have no operating contract — will produce incoherent changes.",
        ))

    if not recon["indicators"].get("has_ci"):
        findings.append(Finding(
            priority="HIGH",
            specialist="platform",
            description="No CI. Every merge is unverified. First integration bug costs 10x to fix in production.",
        ))

    if not recon["indicators"].get("has_dockerfile"):
        findings.append(Finding(
            priority="MEDIUM",
            specialist="platform",
            description="No container definition. Deployment is environment-dependent and unreproducible.",
        ))

    if not recon["indicators"].get("has_decisions"):
        findings.append(Finding(
            priority="LOW",
            specialist="docs",
            description="No DECISIONS.md. Architecture choices are tribal knowledge. Next agent will re-litigate solved problems.",
        ))

    # Append megamind questions as OPPORTUNITY findings for human/agent review
    for q in questions:
        findings.append(Finding(
            priority="OPPORTUNITY",
            specialist="megamind",
            description=q,
        ))

    return findings


# ---------------------------------------------------------------------------
# Report emitter
# ---------------------------------------------------------------------------

def emit_report(recon: dict, wave_results: list[WaveResult], megamind_findings: list[Finding], dry_run: bool) -> None:
    """Print a structured Mastermind run report to stdout."""
    separator = "-" * 72

    print(separator)
    print("MASTERMIND / MEGAMIND BUILD FOUNDRY REPORT")
    print(separator)
    print(f"Project : {recon.get('path', 'unknown')}")
    print(f"Mode    : {'DRY RUN (no changes)' if dry_run else 'PLAN + EXECUTE'}")
    print(f"Languages: {', '.join(recon.get('languages', ['unknown'])) or 'unknown'}")
    print(f"Source files : {recon.get('source_file_count', 0)}")
    print(f"Test files   : {recon.get('test_file_count', 0)}")
    print()

    if recon.get("gaps"):
        print("GAPS DETECTED:")
        for gap in recon["gaps"]:
            print(f"  ✗ {gap}")
        print()

    for wr in wave_results:
        print(f"WAVE {wr.wave}: {wr.wave_name.upper()}")
        if wr.blockers:
            for b in wr.blockers:
                print(f"  BLOCKED: {b}")
        crit = [f for f in wr.findings if f.priority == "CRITICAL"]
        high = [f for f in wr.findings if f.priority == "HIGH"]
        for f in crit + high:
            print(f"  [{f.priority}] [{f.specialist}] {f.description}")
        if wr.actions_taken:
            print("  Actions:")
            for a in wr.actions_taken:
                print(f"    {a}")
        print()

    if megamind_findings:
        print("MEGAMIND CHALLENGER REVIEW:")
        non_opp = [f for f in megamind_findings if f.priority != "OPPORTUNITY"]
        opp = [f for f in megamind_findings if f.priority == "OPPORTUNITY"]
        for f in non_opp:
            print(f"  [{f.priority}] [{f.specialist}] {f.description}")
        if opp:
            print()
            print("  Open questions (OPPORTUNITY):")
            for f in opp:
                print(f"  → {f.description}")
        print()

    print(separator)
    total_critical = sum(wr.critical_count for wr in wave_results)
    total_high = sum(wr.high_count for wr in wave_results)
    mm_critical = sum(1 for f in megamind_findings if f.priority == "CRITICAL")
    mm_high = sum(1 for f in megamind_findings if f.priority == "HIGH")
    print(f"SUMMARY: {total_critical + mm_critical} CRITICAL, {total_high + mm_high} HIGH findings")
    if dry_run:
        print("DRY RUN — no changes made. Remove --dry-run to execute.")
    print(separator)


def emit_json(recon: dict, wave_results: list[WaveResult], megamind_findings: list[Finding]) -> None:
    """Emit machine-readable JSON for downstream agent consumption."""
    output = {
        "recon": recon,
        "waves": [wr.to_dict() for wr in wave_results],
        "megamind": [f.to_dict() for f in megamind_findings],
    }
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_megamind(project_path: Path, start_wave: int = 0, dry_run: bool = False, json_output: bool = False) -> int:
    """Full Mastermind/Megamind execution loop.

    Returns exit code (0 = no critical findings, 1 = critical findings).
    """
    recon = recon_project(project_path)
    if "error" in recon:
        print(f"megamind: error — {recon['error']}", file=sys.stderr)
        return 1

    # Plan waves from start_wave through 10
    wave_results = []
    for wave_num in range(start_wave, 11):
        wr = plan_wave(wave_num, recon)
        wave_results.append(wr)

    # Megamind challenger pass
    megamind_findings = megamind_review(recon)

    if json_output:
        emit_json(recon, wave_results, megamind_findings)
    else:
        emit_report(recon, wave_results, megamind_findings, dry_run)

    total_critical = sum(wr.critical_count for wr in wave_results)
    mm_critical = sum(1 for f in megamind_findings if f.priority == "CRITICAL")
    return 1 if (total_critical + mm_critical) > 0 else 0
