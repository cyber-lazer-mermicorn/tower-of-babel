# Status — tower-of-babel

| Field | Value |
|-------|-------|
| **Status** | Operational-alpha (v1.5) — green |
| **Last verified** | 2026-10-04 |
| **Floors** | 20 |

## Verify results (2026-10-04)

| Command | Result |
|---------|--------|
| `python -m tower validate` | ok (20 floors) |
| `python -m tower generate --check` | ok (regenerated maturity + interfaces) |
| `python -m tower build --all --allow-blocked` | ok |
| `python flagship/run_pipeline.py` | ok |

## Evidence discipline

- Tested floors: behavioral proof on unique advanced boundaries
- Toolchain-gated / service-gated floors: exact blockers declared — no false success
- Lean 4: formally_verified authority invariants

## Next (code only when proof exists)

1. Promote toolchain-gated floors only with CI toolchain installed + green run
2. Keep RECEIPTS.md and VERIFY.md aligned with last green date
3. CANONICAL_POSITION vs GlacierEQ: deferred until dual-exhibit link is sealed

See [VERIFY.md](VERIFY.md) · [RECEIPTS.md](RECEIPTS.md)
