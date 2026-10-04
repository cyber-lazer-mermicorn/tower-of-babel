# Status — tower-of-babel

| Field | Value |
|-------|-------|
| **Status** | Operational-alpha (v1.5) — green + verify chain |
| **Last verified** | 2026-10-04 |
| **Floors** | 20 |

## Real surfaces

- `python -m tower validate`
- `python -m tower generate --check`
- `python -m tower build --all --allow-blocked`
- **`python -m tower verify`** → full chain + writes `quality/last_run.json`
- CI runs verify + language exhibits + uploads receipt artifact

## Evidence discipline

Gated floors remain exact-blocker honest. No false success.

## Next

Promote toolchain-gated floors only when CI installs the toolchain and runs the exhibit green.
