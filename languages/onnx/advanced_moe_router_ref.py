#!/usr/bin/env python3
"""Advanced exhibit: MoE router reference (ONNX-shaped, runtime-gated).

Owns the portable graph boundary for expert routing:
- top-k selection with deterministic tie-break
- explicit admission gate: real ONNX Runtime is optional
- receipt records whether the live runtime was used
No false success. Born to run the reference path always.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass
class RouterReceipt:
    top_k: list[int]
    scores: list[float]
    used_onnx_runtime: bool
    digest: str
    ok: bool
    note: str


def top_k_router(logits: list[float], k: int) -> tuple[list[int], list[float]]:
    if k < 1:
        raise ValueError("k must be >= 1")
    if not logits:
        raise ValueError("logits must be non-empty")
    k = min(k, len(logits))
    indexed = sorted(enumerate(logits), key=lambda t: (-t[1], t[0]))
    chosen = indexed[:k]
    indices = [i for i, _ in chosen]
    scores = [s for _, s in chosen]
    return indices, scores


def run_reference(logits: list[float], k: int = 2) -> RouterReceipt:
    indices, scores = top_k_router(logits, k)
    payload = json.dumps({"idx": indices, "scores": scores, "k": k}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return RouterReceipt(
        top_k=indices,
        scores=scores,
        used_onnx_runtime=False,
        digest=digest,
        ok=True,
        note="pure-Python reference; ONNX Runtime not required for this evidence class",
    )


def try_onnx_runtime() -> bool:
    """Admission probe — never claim success without the dependency."""
    try:
        import onnxruntime  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    logits = [0.1, 0.9, 0.85, 0.2]
    receipt = run_reference(logits, k=2)
    assert receipt.top_k == [1, 2], receipt
    has_ort = try_onnx_runtime()
    print(
        f"advanced_moe_router_ref: ok digest={receipt.digest} "
        f"onnx_runtime={'present' if has_ort else 'absent (gated)'}"
    )
