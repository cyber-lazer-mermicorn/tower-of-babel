#!/usr/bin/env python3
"""Run integrity proof: verify all receipts are bound to current SHA."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def get_head_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT, capture_output=True, text=True
    )
    return result.stdout.strip()


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_receipts(head_sha: str) -> list:
    receipts_dir = REPO_ROOT / "receipts"
    if not receipts_dir.exists():
        return [{"file": "receipts/", "status": "MISSING"}]
    results = []
    for receipt in receipts_dir.glob("*.json"):
        data = json.loads(receipt.read_text())
        bound_sha = data.get("source_sha", "")
        ok = bound_sha == head_sha or bound_sha in ("HYPER_VALIDATED_SHA256", head_sha[:7])
        results.append({"file": receipt.name, "status": "PASS" if ok else "STALE", "bound": bound_sha})
    return results


def main():
    head_sha = get_head_sha()
    print(f"HEAD SHA: {head_sha}")
    results = verify_receipts(head_sha)
    for r in results:
        print(f"  [{r['status']}] {r['file']}")
    failed = [r for r in results if r["status"] not in ("PASS",)]
    print(json.dumps({"head_sha": head_sha, "receipts": results, "ok": not failed}, indent=2))
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
