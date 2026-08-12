#!/usr/bin/env python3
"""Advanced exhibit: isolated weighted evaluation suite with flake budget.

Owns boundary: per-case timeout isolation, weighted metrics, flake-aware
retry within budget, promotion digest. No placeholders.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Case:
    name: str
    fn: Callable[[], Any]
    weight: float = 1.0
    timeout_s: float = 0.5
    expect: Any = True
    max_flakes: int = 1


@dataclass
class CaseResult:
    name: str
    passed: bool
    weight: float
    attempts: int
    detail: str


@dataclass
class SuiteReceipt:
    ok: bool
    score: float
    passed: int
    failed: int
    results: list[CaseResult]
    digest: str
    elapsed_ms: float


def _run_isolated(fn: Callable[[], Any], timeout_s: float) -> tuple[bool, str, Any]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn)
        try:
            val = fut.result(timeout=timeout_s)
            return True, "ok", val
        except concurrent.futures.TimeoutError:
            return False, "timeout", None
        except Exception as e:
            return False, f"error:{type(e).__name__}", None


def run_suite(cases: list[Case]) -> SuiteReceipt:
    t0 = time.monotonic()
    results: list[CaseResult] = []
    score_num = 0.0
    score_den = 0.0
    for case in cases:
        score_den += case.weight
        attempts = 0
        passed = False
        detail = ""
        while attempts <= case.max_flakes and not passed:
            attempts += 1
            ok, detail, val = _run_isolated(case.fn, case.timeout_s)
            if ok and val == case.expect:
                passed = True
                detail = "ok"
            elif ok:
                detail = f"mismatch:{val!r}"
                passed = False
        results.append(
            CaseResult(
                name=case.name,
                passed=passed,
                weight=case.weight,
                attempts=attempts,
                detail=detail,
            )
        )
        if passed:
            score_num += case.weight
    score = (score_num / score_den) if score_den else 0.0
    payload = "|".join(f"{r.name}:{r.passed}:{r.attempts}" for r in results)
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    elapsed = (time.monotonic() - t0) * 1000
    return SuiteReceipt(
        ok=all(r.passed for r in results),
        score=round(score, 4),
        passed=sum(1 for r in results if r.passed),
        failed=sum(1 for r in results if not r.passed),
        results=results,
        digest=digest,
        elapsed_ms=round(elapsed, 2),
    )


def _demo() -> SuiteReceipt:
    def good() -> bool:
        return True

    def flaky() -> bool:
        if not hasattr(flaky, "n"):
            flaky.n = 0  # type: ignore[attr-defined]
        flaky.n += 1  # type: ignore[attr-defined]
        if flaky.n < 2:
            raise RuntimeError("flake")
        return True

    def bad() -> bool:
        return False

    cases = [
        Case("truth", good, weight=2.0),
        Case("flaky_ok", flaky, weight=1.0, max_flakes=2),
        Case("expect_fail", bad, weight=1.0, expect=False),
    ]
    return run_suite(cases)


if __name__ == "__main__":
    r = _demo()
    assert r.passed >= 2
    print(
        f"advanced_eval_harness: ok digest={r.digest} score={r.score} "
        f"passed={r.passed} failed={r.failed} elapsed_ms={r.elapsed_ms}"
    )
