# Quality Contract

The Tower is a governed systems portfolio, not a file-extension collection.  
Every exhibit must state truthfully what it proves and which limitations remain.

## Canonical authority

`registry/tower.yml` is the sole authored technology authority.  
Generated maturity, interface, and build surfaces derive from it.

## Easy exhibits

Must:
- teach one technology-specific concept with minimal ceremony
- parse, compile, or execute with the documented toolchain when available
- be deterministic and safe for the demonstrated input
- avoid claiming production readiness

## Advanced exhibits

Must include:
1. Clear W4H+How rationale
2. Typed or explicit inputs and outputs
3. Validation and failure behavior for malformed / unsafe input
4. A meaningful invariant or policy boundary
5. Observability (metrics, receipts, structured report)
6. A runnable demonstration, proof, benchmark, or test vector
7. No placeholders (`pass`, empty bodies, unconditional success)
8. Bounded resource behavior where concurrency, memory, or untrusted input is involved

An advanced exhibit need not be a complete product. It must be honest evidence of the capability named in the registry.

## Evidence and blockers

- Stronger evidence states require corresponding execution evidence.
- Missing toolchains, services, or hardware produce **exact blockers**, never false success.
- Structural presence is not compiler proof. Compiler proof is not production proof.

## Promotion rule

A capability becomes active only after its declared evidence gate succeeds.  
Branch completion is not promotion.
