# Harden & Verify Pass

_Last verified narrative: 2026-08-12 · Docs touch: 2026-08-31_

## CLI

```bash
python -m pip install -e ".[dev]"
python -m tower validate
python -m tower generate --check
python -m tower build --all --allow-blocked
python flagship/run_pipeline.py
```

Reported results (2026-08-12):
- `validate: ok (20 floors)`
- `generate --check: ok`
- `build --all --allow-blocked: ok`

## Exhibit self-checks (local)

| Exhibit | Result |
|---------|--------|
| Python easy + advanced (circuit breaker) | ok |
| Eval harness (flake budget) | ok |
| ONNX temperature router | ok |
| Triton fused attention ref | ok |
| Rust safety governor | ok |
| Go telemetry decoder | ok |
| C++ TTL score cache | ok |
| Java bounded work queue | ok |
| TypeScript MCP gateway | ok |
| Flagship pipeline | ok |

## Evidence discipline

Gated floors remain exact-blocker honest. No false success.

## Constellation link

Grove STATUS (2026-08-31) tracks Tower as **operational-alpha** with gates through `NERVOUS_SYSTEM_DOCUMENTED` pass; `CANONICAL_POSITION_RESOLVED` still pending.

Connector map: [constellation-map](https://github.com/cyber-lazer-mermicorn/constellation-map).

## Next (code)

- Re-run validate/build on current main when toolchains change
- Optional toolchains for gated floors only with proof
- Keep RECEIPTS.md aligned with last green run
