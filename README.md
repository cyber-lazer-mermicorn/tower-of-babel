# Tower of Babel

> **AI Systems Engineering Rosetta Stone**  
> Built for high-signal remote AI development roles.

[![Status](https://img.shields.io/badge/status-operational--alpha-blue)](https://github.com/cyber-lazer-mermicorn/tower-of-babel)
[![Evidence](https://img.shields.io/badge/evidence-gates-green)](quality/exhibit_status.json)

This repository is a **governed technology map** for modern AI systems work.  
It does not collect languages for decoration. It places technologies by measurable boundary advantage, supplies dual exhibits (easy + advanced), declares evidence state, and produces recruiter-readable proof.

**Primary audience**: hiring managers and technical interviewers evaluating candidates for remote AI / ML / agent / systems roles.

**Secondary audience**: operators and agents that need an honest, machine-readable technology contract.

---

## Why this exists

Most polyglot repos are resume theater.  
This Tower is designed so a recruiter or interviewer can answer in under two minutes:

1. What can this person actually build?
2. How do they choose tools under constraints?
3. Can they prove claims instead of asserting them?
4. Do they understand boundaries (safety, cost, latency, ownership)?

Every floor answers **What / Where / When / Why / How** and carries an evidence class.

---

## The high-signal stack (v1 floors)

Focused set optimized for 2026 AI remote roles. Expand only when a new floor earns a unique boundary.

| # | Technology | Class | Core boundary | Evidence | Easy | Advanced |
|---|------------|-------|---------------|----------|------|----------|
| 1 | **Python** | orchestration + AI | Agents, evaluation, control planes, rapid composition | `tested` | [easy](languages/python/easy_fibonacci.py) | [advanced_async_orchestrator.py](languages/python/advanced_async_orchestrator.py) |
| 2 | **TypeScript** | typed interfaces | MCP/JSON-RPC gateways, browser + Node agents, contracts | `tested` | [easy](languages/typescript/easy_greet.ts) | [advanced_mcp_gateway.ts](languages/typescript/advanced_mcp_gateway.ts) |
| 3 | **Rust** | safety + systems | Authority governors, memory-safe side-effect control | `tested` | [easy](languages/rust/easy_counter.rs) | [advanced_safety_governor.rs](languages/rust/advanced_safety_governor.rs) |
| 4 | **Go** | concurrent services | Telemetry, gateways, simple deployable workers | `tested` | [easy](languages/go/easy_ping.go) | [advanced_telemetry_decoder.go](languages/go/advanced_telemetry_decoder.go) |
| 5 | **SQL + vectors** | durable state | Canonical store, embeddings, constraints, RLS patterns | `service_gated` | [easy](languages/sql/easy_table.sql) | [advanced_pgvector_hnsw.sql](languages/sql/advanced_pgvector_hnsw.sql) |
| 6 | **WebAssembly** | sandbox | Capability-bounded tool execution | `tested` | [easy](languages/wat/easy_add.wat) | [advanced_wasm_sandbox.wat](languages/wat/advanced_wasm_sandbox.wat) |
| 7 | **Protocol Buffers** | contracts | Cross-language mission envelopes + receipts | `tested` | [easy](languages/protobuf/easy_user.proto) | [advanced_mission_receipt.proto](languages/protobuf/advanced_mission_receipt.proto) |
| 8 | **Lean 4** | formal | Receipt-chain / authority invariants (when required) | `formally_verified` | [easy](languages/lean4/easy_logic.lean) | [advanced_truth_gate.lean](languages/lean4/advanced_truth_gate.lean) |

Additional floors (CUDA/Triton awareness, ONNX, eBPF, etc.) are admitted only when they own a non-duplicated boundary and carry real evidence.

---

## Flagship polyglot AI mission

A single end-to-end path that hiring managers can run or inspect:

```text
TypeScript ingress (typed request)
    → Protocol Buffers mission contract
Python planner + evaluation harness
    → capability plan + scores
Rust safety governor
    → allow / block decision
Go telemetry emitter
    → structured events
SQL canonical state
    → durable mission + receipt
WebAssembly sandbox
    → constrained tool boundary
Lean 4 (optional)
    → receipt invariant
Tower receipt
```

See `flagship/` and run:

```bash
python flagship/run_pipeline.py
```

---

## Quick start

```bash
# Install
python -m pip install -e ".[dev]"

# Validate registry + exhibits
python -m tower validate

# Generate derived surfaces
python -m tower generate --check

# Run portable builds (blocked floors report exact reasons)
python -m tower build --all --allow-blocked

# Flagship pipeline
python flagship/run_pipeline.py
```

---

## Evidence classes (truthful language only)

| State | Meaning |
|-------|---------|
| `illustrative` | Teaches concept. No runtime claim. |
| `compiles` | Pinned toolchain accepts the exhibit. |
| `tested` | Automated behavioral checks pass. |
| `benchmark` | Reproducible performance number exists. |
| `hardware_gated` / `toolchain_gated` / `service_gated` | Present but blocked by declared dependency. |
| `formally_verified` | Proof kernel accepts the claim. |
| `integrated` | Participates in the flagship pipeline. |
| `production_reference` | Operational failure handling + observability evidence. |

Never promote a floor without matching evidence.

---

## Architecture contract

- `registry/tower.yml` is the sole authored authority.
- Generated files (`generated/`, README matrix sections) are never hand-edited.
- Advanced exhibits must own a real boundary, show failure behavior, and emit observable results.
- Exact blockers > false success.
- Cross-language interfaces are versioned and explicit.

See `AGENTS.md`, `QUALITY_CONTRACT.md`, and `docs/`.

---

## For recruiters & interviewers

This repository is deliberately small and high-signal.  
It demonstrates:

- Tool selection under constraint
- Multi-language composition with contracts
- Safety and authority boundaries
- Evaluation and receipt thinking
- Ability to say “not yet proven” instead of overclaiming

If you are evaluating for a remote AI systems / agent / platform role, start with:

1. `flagship/run_pipeline.py`
2. The advanced exhibits for Python, TypeScript, and Rust
3. `QUALITY_CONTRACT.md`

---

## Rights

All original code, designs, writing, and commercial concepts in this repository are **proprietary**.  
All rights reserved. Collaboration is welcome through explicit discussion.  
No open-source license is granted by default.

---

## Status

**Operational-alpha.**  
Core floors and flagship path are present and intentional.  
Expansion is gated by unique boundary + evidence, not by desire for more languages.
