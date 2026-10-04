# Local verification receipts

## 2026-10-04 (completion pass)

| Surface | Result |
|---------|--------|
| `PYTHONPATH=src python -m tower validate` | ok (20 floors) |
| `python -m tower generate --check` | ok (drift fixed; maturity + interfaces committed) |
| `python -m tower build --all --allow-blocked` | ok |
| `python flagship/run_pipeline.py` | ok |

Gated floors remain exact-blocker honest.

## 2026-08-31 (sandbox re-run)

| Surface | Result |
|---------|--------|
| `PYTHONPATH=src python -m tower validate` | ok (20 floors) |
| `python -m tower generate --check` | ok |
| `python -m tower build --all --allow-blocked` | ok |

## Prior (v1.5 skill-up)

| Surface | Result |
|---------|--------|
| Python circuit breaker orchestrator | ok |
| Rust capability governor | ok |
| Go telemetry metrics | ok |
| TypeScript idempotent MCP gateway | ok |
| Eval flake budget harness | ok |
| C++ TTL score cache | ok |
| ONNX temperature router | ok |
| Flagship pipeline | ok |
| `tower validate` | ok (20 floors) |
