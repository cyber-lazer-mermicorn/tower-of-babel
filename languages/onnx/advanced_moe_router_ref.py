#!/usr/bin/env python3
"""Advanced exhibit: deterministic MoE router reference with temperature.

Owns model-format boundary: top-k expert selection, temperature shaping,
ORT admission probe, sealed receipt. Host path always runs; ORT is optional.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass


@dataclass
class RouterReceipt:
    experts: list[int]
    weights: list[float]
    used_ort: bool
    digest: str
    ok: bool
    note: str


def softmax(xs: list[float], temperature: float = 1.0) -> list[float]:
    if temperature <= 0:
        raise ValueError("temperature must be > 0")
    scaled = [x / temperature for x in xs]
    m = max(scaled)
    exps = [math.exp(x - m) for x in scaled]
    z = sum(exps)
    if z <= 0:
        raise ValueError("invalid softmax")
    return [e / z for e in exps]


def top_k_route(
    logits: list[float],
    k: int,
    temperature: float = 1.0,
) -> tuple[list[int], list[float]]:
    if k <= 0 or k > len(logits):
        raise ValueError("k out of range")
    weights = softmax(logits, temperature)
    ranked = sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)
    experts = ranked[:k]
    chosen = [weights[i] for i in experts]
    s = sum(chosen)
    chosen = [w / s for w in chosen]
    return experts, chosen


def ort_available() -> bool:
    try:
        import onnxruntime  # noqa: F401

        return True
    except Exception:
        return False


def run_router(logits: list[float], k: int = 2, temperature: float = 1.0) -> RouterReceipt:
    experts, weights = top_k_route(logits, k, temperature)
    used = ort_available()
    payload = f"{experts}|{[round(w, 6) for w in weights]}|{temperature}|{used}"
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    note = "ORT present" if used else "host reference only; ORT not installed"
    return RouterReceipt(
        experts=experts,
        weights=weights,
        used_ort=used,
        digest=digest,
        ok=True,
        note=note,
    )


if __name__ == "__main__":
    logits = [0.1, 2.5, 0.3, 1.2, 0.05]
    r = run_router(logits, k=2, temperature=0.8)
    assert r.ok and len(r.experts) == 2
    assert r.experts[0] == 1
    r2 = run_router(logits, k=2, temperature=2.0)
    assert r2.ok
    print(f"advanced_moe_router_ref: ok digest={r.digest} experts={r.experts} ort={r.used_ort}")
