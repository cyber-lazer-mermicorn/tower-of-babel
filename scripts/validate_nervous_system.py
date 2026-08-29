#!/usr/bin/env python3
"""End-to-end nervous system health validator."""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PASS = "PASS"
FAIL = "FAIL"


def check(label: str, ok: bool, detail: str = "") -> dict:
    status = PASS if ok else FAIL
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    return {"label": label, "status": status, "detail": detail}


def run_validate() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "tower", "validate"],
        cwd=REPO_ROOT, capture_output=True, text=True
    )
    return result.returncode == 0


def check_registry() -> bool:
    return (REPO_ROOT / "registry" / "tower.yml").exists()


def check_machine_layer() -> bool:
    required = [
        "machine/capabilities.json",
        "machine/promotion_authority.json",
        "machine/target-contract.json",
        "machine/excellence-state.json",
    ]
    return all((REPO_ROOT / p).exists() for p in required)


def check_governance_docs() -> bool:
    required = [
        "AGENTS.md", "QUALITY_CONTRACT.md", "ARCHITECTURE_LAW.md",
        "BRANCH_POLICY.md", "NERVOUS_SYSTEM.md",
    ]
    return all((REPO_ROOT / p).exists() for p in required)


def check_no_generated_drift() -> bool:
    result = subprocess.run(
        ["git", "diff", "--name-only", "generated/"],
        cwd=REPO_ROOT, capture_output=True, text=True
    )
    return result.stdout.strip() == ""


def main():
    print("\n=== Tower Nervous System Validation ===")
    results = [
        check("Registry exists", check_registry()),
        check("Machine layer complete", check_machine_layer()),
        check("Governance docs present", check_governance_docs()),
        check("Registry validates", run_validate()),
        check("No generated drift", check_no_generated_drift()),
    ]
    failed = [r for r in results if r["status"] == FAIL]
    print(f"\nResult: {'OPERATIONAL' if not failed else 'DEGRADED'}")
    print(json.dumps({"checks": results, "status": "OPERATIONAL" if not failed else "DEGRADED"}, indent=2))
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
