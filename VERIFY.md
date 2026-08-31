# Harden & Verify Pass

_Last green run: 2026-08-31_

## CLI

```bash
python -m pip install -e ".[dev]"
# or without install:
PYTHONPATH=src python -m tower validate
PYTHONPATH=src python -m tower generate --check
PYTHONPATH=src python -m tower build --all --allow-blocked
python flagship/run_pipeline.py
```

## Results (2026-08-31)

- `validate: ok (20 floors)`
- `generate --check: ok`
- `build --all --allow-blocked: ok`

## Evidence discipline

Gated floors remain exact-blocker honest. No false success.

## Constellation link

Grove STATUS tracks Tower as operational-alpha. Connector: [constellation-map](https://github.com/cyber-lazer-mermicorn/constellation-map).

## Next (code)

- Keep RECEIPTS.md aligned with last green run
- Promote gated floors only with toolchain proof
