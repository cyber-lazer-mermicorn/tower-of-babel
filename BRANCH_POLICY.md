# Branch Policy

## Canonical branch

`main` is the only permanent branch. It must always be green.

## Work branches

All work happens on short-lived branches:

```
feat/<slug>      # new capability or exhibit
fix/<slug>       # correctness fix
harden/<slug>    # quality gate hardening
chore/<slug>     # non-functional maintenance
```

Branches older than 7 days without a PR are stale and may be deleted.

## Merge rules

- No direct push to `main`
- PR must pass: `python -m tower validate` + `python -m tower build --all --allow-blocked` + all tests
- Generated drift must be zero at merge time
- Receipt must be emitted and bound before merge

## Force push policy

Force push is **never permitted** on `main`.  
Force push on work branches is allowed only before PR is opened.

## Tagging

Tags follow `vMAJOR.MINOR.PATCH`. Only `main` HEAD is tagged.  
Tags are immutable once pushed.
