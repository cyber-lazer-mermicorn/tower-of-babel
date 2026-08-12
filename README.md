# Tower of Babel

> **AI Systems Engineering Rosetta Stone**  
> Built for high-signal remote AI development roles.

[![Status](https://img.shields.io/badge/status-operational--alpha-blue)](https://github.com/cyber-lazer-mermicorn/tower-of-babel)
[![Evidence](https://img.shields.io/badge/evidence-gates-green)](quality/exhibit_status.json)
[![CI](https://github.com/cyber-lazer-mermicorn/tower-of-babel/actions/workflows/tower.yml/badge.svg)](https://github.com/cyber-lazer-mermicorn/tower-of-babel/actions/workflows/tower.yml)

This repository is a **governed technology map** for modern AI systems work.  
It places technologies by measurable boundary advantage, supplies dual exhibits (easy + advanced), declares evidence state, and produces recruiter-readable proof.

**Primary audience**: hiring managers and technical interviewers for remote AI / ML / agent / systems roles.

**Secondary audience**: operators and agents that need an honest, machine-readable technology contract.

---

## Complementary to the broader systems Tower

This repository is **AI-job-optimized signal**.  
A related, broader multi-language systems engineering Rosetta Stone lives at  
[GlacierEQ/the-tower-of-babel](https://github.com/GlacierEQ/the-tower-of-babel).

| Surface | Focus |
|---------|--------|
| **This Tower** | High-signal stack for remote AI / agent / platform roles |
| **GlacierEQ Tower** | Wide systems map (40 floors), formal methods, hardware/GPU/HDL |

They are complementary, not competitive.

---

## Why this exists

Most polyglot repos are resume theater.  
This Tower is designed so a recruiter can answer in under two minutes:

1. What can this person actually build?
2. How do they choose tools under constraints?
3. Can they prove claims instead of asserting them?
4. Do they understand boundaries (safety, cost, latency, ownership)?

Every floor answers **What / Where / When / Why / How** and carries an evidence class.

---

## The high-signal stack (v1.2 — 14 floors)

Each floor owns a non-duplicated boundary. Expand only with unique value + evidence.

| # | Technology | Core boundary | Evidence | Advanced exhibit |
|---|------------|---------------|----------|------------------|
| 1 | **Python** | Agents, evaluation, control planes | `tested` | [async orchestrator](languages/python/advanced_async_orchestrator.py) |
| 2 | **TypeScript** | MCP/JSON-RPC gateways, contracts | `tested` | [MCP gateway](languages/typescript/advanced_mcp_gateway.ts) |
| 3 | **Rust** | Authority governors, fail-closed policy | `tested` | [safety governor](languages/rust/advanced_safety_governor.rs) |
| 4 | **Go** | Telemetry trust boundary | `tested` | [telemetry decoder](languages/go/advanced_telemetry_decoder.go) |
| 5 | **C++** | Bounded score cache, utility eviction | `tested` | [KV score cache](languages/cpp/advanced_kv_score_cache.cpp) |
| 6 | **Java** | Bounded work queue, abort policy | `tested` | [work queue](languages/java/advanced_bounded_work_queue.java) |
| 7 | **Evaluation Harness** | Isolated scoring + promotion digests | `tested` | [eval harness](languages/eval/advanced_eval_harness.py) |
| 8 | **ONNX (reference)** | Portable router + ORT probe | `tested` | [MoE router](languages/onnx/advanced_moe_router_ref.py) |
| 9 | **Triton (reference)** | Fused attention oracle (GPU gated) | `tested` | [fused attention](languages/triton/advanced_fused_attention_ref.py) |
| 10 | **Julia** | Energy-audited orbital integration | `toolchain_gated` | [Verlet orbit](languages/julia/advanced_orbital_verlet.jl) |
| 11 | **SQL + vectors** | Canonical store, HNSW patterns | `service_gated` | [pgvector patterns](languages/sql/advanced_pgvector_hnsw.sql) |
| 12 | **WebAssembly** | Capability-bounded tools | `tested` | [WASM sandbox](languages/wat/advanced_wasm_sandbox.wat) |
| 13 | **Protocol Buffers** | Mission + receipt envelopes | `tested` | [mission receipt](languages/protobuf/advanced_mission_receipt.proto) |
| 14 | **Lean 4** | Authority / receipt invariants | `formally_verified` | [truth gate](languages/lean4/advanced_truth_gate.lean) |

---

## Flagship polyglot AI mission

```text
TypeScript ingress → Proto mission → Python plan + eval
  → Rust governor → Go telemetry → receipt
```

```bash
python flagship/run_pipeline.py
```

Local verification: [`RECEIPTS.md`](RECEIPTS.md).

---

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m tower validate
python -m tower generate --check
python -m tower build --all --allow-blocked
python flagship/run_pipeline.py
```

---

## Evidence classes

| State | Meaning |
|-------|---------|
| `tested` | Automated behavioral checks pass |
| `toolchain_gated` / `service_gated` / `hardware_gated` | Present; exact blocker declared |
| `formally_verified` | Proof kernel accepts the claim |

Never promote without matching evidence. Exact blockers > false success.

---

## For recruiters & interviewers

Start with:

1. `flagship/run_pipeline.py`
2. Advanced exhibits: Python orchestrator, Eval harness, TypeScript gateway, Rust governor, C++ cache
3. `docs/JOB_APPLICATION_SURFACE.md`

Talking points emphasize tool selection under constraint, evaluation discipline, and honest gated floors.

---

## Rights

All original code, designs, writing, and commercial concepts are **proprietary**.  
All rights reserved. Collaboration welcome through explicit discussion.

---

## Status

**Operational-alpha (v1.2).**  
Fourteen floors with unique boundaries, dual exhibits, CI, and flagship path.  
Expansion is gated by unique boundary + evidence.
