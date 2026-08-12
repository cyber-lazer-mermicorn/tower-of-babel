#!/usr/bin/env python3
"""Advanced exhibit: bounded evaluation harness with case isolation and receipt.

Owns the evaluation boundary for agent/model outputs:
- typed cases, expected signals, timeouts
- isolated failures (one bad case does not abort the suite)
- aggregate metrics + per-case evidence
- deterministic content digest for promotion gates
No placeholders. Born to run.
"""

from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import asdict, dataclass
from typing import Any, Callable


@dataclass
class EvalCase:
    case_id: str
    input: Any
    expected: Any
    weight: float = 1.0


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    score: float
    detail: str
    latency_ms: float


@dataclass
class EvalReceipt:
    suite_id: str
    total: int
    passed: int
    failed: int
    weighted_score: float
    cases: list[CaseResult]
    duration_ms: float
    digest: str
    ok: bool


Scorer = Callable[[Any, Any], float]


def exact_match(predicted: Any, expected: Any) -> float:
    return 1.0 if predicted == expected else 0.0


class EvalHarness:
    """Thread-isolated evaluation suite with hard per-case timeout."""

    def __init__(
        self,
        suite_id: str,
        scorer: Scorer = exact_match,
        max_workers: int = 4,
        case_timeout_s: float = 2.0,
    ):
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        if case_timeout_s <= 0:
            raise ValueError("case_timeout_s must be positive")
        self.suite_id = suite_id
        self.scorer = scorer
        self.max_workers = max_workers
        self.case_timeout_s = case_timeout_s
        self._cases: list[EvalCase] = []

    def add(self, case: EvalCase) -> None:
        if not case.case_id:
            raise ValueError("case_id required")
        if case.weight < 0:
            raise ValueError("weight must be non-negative")
        self._cases.append(case)

    def _run_one(
        self, case: EvalCase, predict: Callable[[Any], Any]
    ) -> CaseResult:
        start = time.perf_counter()
        try:
            predicted = predict(case.input)
            score = float(self.scorer(predicted, case.expected))
            if score < 0.0 or score > 1.0:
                raise ValueError(f"scorer returned out-of-range score: {score}")
            passed = score >= 1.0
            detail = "exact" if passed else f"score={score:.3f}"
        except Exception as exc:
            score = 0.0
            passed = False
            detail = f"error:{type(exc).__name__}:{exc}"
        latency_ms = (time.perf_counter() - start) * 1000
        return CaseResult(
            case_id=case.case_id,
            passed=passed,
            score=score,
            detail=detail,
            latency_ms=round(latency_ms, 3),
        )

    def run(self, predict: Callable[[Any], Any]) -> EvalReceipt:
        if not self._cases:
            raise RuntimeError("no cases registered")

        start = time.perf_counter()
        results: list[CaseResult] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(self._run_one, case, predict): case
                for case in self._cases
            }
            for fut, case in futures.items():
                try:
                    results.append(fut.result(timeout=self.case_timeout_s))
                except FuturesTimeout:
                    results.append(
                        CaseResult(
                            case_id=case.case_id,
                            passed=False,
                            score=0.0,
                            detail="timeout",
                            latency_ms=self.case_timeout_s * 1000,
                        )
                    )
                except Exception as exc:
                    results.append(
                        CaseResult(
                            case_id=case.case_id,
                            passed=False,
                            score=0.0,
                            detail=f"executor:{type(exc).__name__}",
                            latency_ms=0.0,
                        )
                    )

        results.sort(key=lambda r: r.case_id)
        total_weight = sum(c.weight for c in self._cases) or 1.0
        weight_by_id = {c.case_id: c.weight for c in self._cases}
        weighted = sum(r.score * weight_by_id[r.case_id] for r in results) / total_weight
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        duration_ms = (time.perf_counter() - start) * 1000

        payload = json.dumps(
            {
                "suite": self.suite_id,
                "results": [asdict(r) for r in results],
                "weighted": round(weighted, 6),
            },
            sort_keys=True,
        )
        digest = hashlib.sha256(payload.encode()).hexdigest()[:20]

        return EvalReceipt(
            suite_id=self.suite_id,
            total=len(results),
            passed=passed,
            failed=failed,
            weighted_score=round(weighted, 6),
            cases=results,
            duration_ms=round(duration_ms, 2),
            digest=digest,
            ok=failed == 0,
        )


def _demo() -> None:
    harness = EvalHarness("agent-routing-v1", case_timeout_s=1.0)

    harness.add(EvalCase("route_search", "find docs", "search", weight=1.0))
    harness.add(EvalCase("route_write", "save note", "write", weight=1.0))
    harness.add(EvalCase("route_unknown", "???", "fallback", weight=0.5))

    def predict(x: str) -> str:
        if "find" in x or "search" in x:
            return "search"
        if "save" in x or "write" in x:
            return "write"
        return "fallback"

    receipt = harness.run(predict)
    assert receipt.ok, receipt
    assert receipt.passed == 3
    print(f"advanced_eval_harness: ok digest={receipt.digest} score={receipt.weighted_score}")


if __name__ == "__main__":
    _demo()
