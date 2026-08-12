#!/usr/bin/env python3
"""Advanced exhibit: fused single-query attention reference (host math).

Owns the kernel-boundary idea: one fused pass over Q·K scores + softmax + V.
Real Triton/CUDA launch is hardware_gated — this path always runs as the
oracle and records that the accelerator was not used.
No placeholders. Born to run the reference.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass


@dataclass
class AttentionReceipt:
    output: list[float]
    used_accelerator: bool
    digest: str
    ok: bool
    note: str


def fused_attention(
    q: list[float],
    k: list[list[float]],
    v: list[list[float]],
) -> list[float]:
    if not k or not v or len(k) != len(v):
        raise ValueError("k and v must be non-empty and aligned")
    d = len(q)
    if d == 0:
        raise ValueError("q must be non-empty")
    for row in k:
        if len(row) != d:
            raise ValueError("k row dim mismatch")
    dv = len(v[0])
    for row in v:
        if len(row) != dv:
            raise ValueError("v row dim mismatch")

    scale = 1.0 / math.sqrt(d)
    scores = [sum(q[j] * k[i][j] for j in range(d)) * scale for i in range(len(k))]
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    z = sum(exps)
    if z <= 0:
        raise ValueError("softmax denominator invalid")
    weights = [e / z for e in exps]
    out = [0.0] * dv
    for i, w in enumerate(weights):
        for j in range(dv):
            out[j] += w * v[i][j]
    return out


def run_reference(
    q: list[float],
    k: list[list[float]],
    v: list[list[float]],
) -> AttentionReceipt:
    out = fused_attention(q, k, v)
    payload = f"{out}|{len(k)}|{len(q)}"
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return AttentionReceipt(
        output=out,
        used_accelerator=False,
        digest=digest,
        ok=True,
        note="host reference only; Triton/CUDA launch requires declared GPU evidence",
    )


if __name__ == "__main__":
    q = [1.0, 0.0]
    k = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
    v = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
    r = run_reference(q, k, v)
    assert r.ok and len(r.output) == 2
    assert r.output[0] > r.output[1]
    print(f"advanced_fused_attention_ref: ok digest={r.digest}")
