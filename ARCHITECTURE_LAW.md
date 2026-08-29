# Architecture Law

This document is binding. No agent, human, or automation may bypass it.

## Monolith law

The Tower is a single deployable monolith projection.  
No microservice split, no package extraction, no sub-repo is permitted without explicit estate-role resolution.

## Registry supremacy

`registry/tower.yml` is the only source of truth for technology admission, placement, and evidence state.  
No other file may assert a technology's maturity, readiness, or canonical path.

## Layer contracts

| Layer | Purpose | Mutation rule |
|---|---|---|
| `languages/` | Language exhibits (easy + advanced) | Registry-gated only |
| `flagship/` | Production-grade showcase | Must pass all quality gates |
| `frontier/` | Experimental — no promotion guarantee | Clearly marked, never cited as evidence |
| `src/` | Core mechanism | Central mechanism only, no sprawl |
| `machine/` | Autonomous state and promotion authority | Machine-written, never hand-edited |
| `generated/` | Generated surfaces | Never hand-edited, overwritten by generate step |
| `quality/` | Quality metrics and scores | Derived, never authored |
| `registry/` | Canonical technology registry | Single authored source |

## Frontier rule

Frontier code is exploratory. It carries no evidence weight.  
Promotion from frontier to flagship requires a full quality gate pass and registry update.

## Naming law

File names must be lowercase, hyphen-separated.  
No abbreviations that obscure meaning. No generic names (`utils`, `helpers`, `misc`).

## Drift rule

Generated surfaces must not diverge from the registry for more than one commit.  
Drift detected at review time blocks merge.
