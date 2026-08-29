# Megamind — Autonomous Build Foundry

The Mastermind/Megamind system is a two-role autonomous build director built into the Tower CLI.

## Roles

| Role | Runs | Purpose |
|------|------|---------|
| **Mastermind** | Every wave | Continuous builder and integrator. Knows the evolving implementation deeply. Owns shared reality. |
| **Megamind** | At wave boundaries | Periodic whole-system challenger. Arrives with fresh eyes. Asks what the Mastermind can’t see. |

Together:
```
BUILD → CHALLENGE → RECOMPOSE → BUILD BETTER
```

---

## Usage

```bash
# Full run from Wave 0 (recon) through Wave 10 (genius pass)
python -m tower megamind --project /path/to/your/project

# Start at a specific wave (e.g. you’re already at Wave 3 — Harden)
python -m tower megamind --project . --wave 3

# Dry run — analyse and report, make no changes
python -m tower megamind --project . --dry-run

# Machine-readable JSON output for downstream agent consumption
python -m tower megamind --project . --json | jq '.megamind'

# Run against the Tower of Babel repo itself
python -m tower megamind
```

---

## Wave Sequence

| Wave | Name | Key question |
|------|------|--------------|
| 0 | Reconnaissance | What exists, what works, what is missing? |
| 1 | Make It Run | Does the system run end-to-end? |
| 2 | Complete Core Loop | Does the defining user workflow complete? |
| 3 | Harden | Does it survive common failures? |
| 4 | Professionalize | Can a new engineer operate it without tribal knowledge? |
| 5 | Performance | Are the largest bottlenecks addressed? |
| 6 | Advanced Capability | Is the ceiling raised? |
| 7 | Polish | Does it feel designed rather than accumulated? |
| 8 | Adversarial Review | Have we tried to break it? |
| 9 | Deployment Proof | Does the production deployment actually work? |
| 10 | Genius Pass | What would an elite engineer improve with another month? |

---

## Megamind Questions (Wave 10 / boundary reviews)

1. What is architecturally weak?
2. What subsystem is holding back the rest?
3. What capability is unexpectedly close to becoming possible?
4. What complexity can be eliminated?
5. What valuable components are not yet connected?
6. What single redesign would produce the highest leverage?

---

## Priority Engine

Candidates are scored:

```
score = (IMPACT × CONFIDENCE × LEVERAGE × URGENCY) / COST
```

All inputs 0.0–1.0. Highest score = do this first.

Also weigh:
- Dependency blocking (unblocks other work)
- Technical risk (reversibility)
- Architectural leverage (one change unlocks many)

---

## Integration with Tower Registry

The Megamind respects Tower’s existing doctrine:
- `registry/tower.yml` remains the single authority for language admission and evidence state
- `python -m tower validate` must pass before any megamind wave progresses past Wave 1
- Generated files (`generated/`) are never hand-edited
- The foundry’s specialist instructions live in `.github/instructions/` (per-project)

---

## Absolute Rule

> Optimize for **strongest working system**, not most files changed, most agents used, or largest architecture.

A feature exists only when its real execution path works.
