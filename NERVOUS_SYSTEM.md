# Nervous System

The Tower's nervous system is the set of automated checks that keep it honest.

## Components

| Component | File | Purpose |
|---|---|---|
| Registry validator | `python -m tower validate` | Ensures `registry/tower.yml` is schema-valid and internally consistent |
| Generator | `python -m tower generate` | Derives all generated surfaces from the registry |
| Builder | `python -m tower build` | Attempts to compile/run each exhibit; records exact blockers |
| Megamind | `python -m tower megamind` | Autonomous build foundry director — orchestrates the full pipeline |
| Integrity proof | `scripts/run_integrity_proof.py` | Verifies SHA receipts and integrity state |
| Nervous system validator | `scripts/validate_nervous_system.py` | End-to-end health check across all layers |
| Mastermind sidecar | `scripts/mastermind_sidecar.py` | Emits live telemetry JSON — derived, never hardcoded |

## Health states

- `OPERATIONAL` — all integrity checks pass, registry and generated surfaces in sync
- `DEGRADED` — one or more integrity checks fail; details in telemetry output
- `DRIFT` — generated surfaces have diverged from registry

## Runbook

```bash
# Full health check
python scripts/validate_nervous_system.py

# Live telemetry
python scripts/mastermind_sidecar.py

# Full pipeline (validate → generate → build → receipt)
python -m tower megamind
```

## Invariants

- Telemetry counts are always derived from the registry, never hardcoded
- A `DEGRADED` state blocks all merges
- Receipts are bound to the exact commit SHA at emit time
