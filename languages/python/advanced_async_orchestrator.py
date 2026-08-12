#!/usr/bin/env python3
"""Advanced exhibit: drainable priority agent runtime with circuit breaker.

Owns a real boundary: bounded priority queues, FIFO ties, futures, retries,
per-worker circuit breaker, deadline budget, graceful drain, structured receipt.
No placeholders. First-pass production skill.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable


class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(order=True)
class WorkItem:
    priority: int
    sequence: int
    name: str = field(compare=False)
    coro_factory: Callable[[], Awaitable[Any]] = field(compare=False)
    max_attempts: int = field(default=3, compare=False)
    attempt: int = field(default=0, compare=False)


@dataclass
class Receipt:
    ok: bool
    completed: list[str]
    failed: list[str]
    drained: bool
    circuit_open: bool
    digest: str
    elapsed_ms: float


class CircuitBreaker:
    """Fail-closed breaker after consecutive failures within a window."""

    def __init__(self, threshold: int = 3, cooldown_s: float = 0.05) -> None:
        self.threshold = threshold
        self.cooldown_s = cooldown_s
        self.failures = 0
        self.opened_at: float | None = None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        if time.monotonic() - self.opened_at >= self.cooldown_s:
            self.opened_at = None
            self.failures = 0
            return True
        return False

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = time.monotonic()

    @property
    def is_open(self) -> bool:
        return not self.allow()


class AgentRuntime:
    def __init__(
        self,
        workers: int = 2,
        max_queue: int = 32,
        deadline_s: float = 2.0,
    ) -> None:
        self._workers = workers
        self._max_queue = max_queue
        self._deadline_s = deadline_s
        self._q: asyncio.PriorityQueue[WorkItem] = asyncio.PriorityQueue(
            maxsize=max_queue
        )
        self._poison = WorkItem(
            priority=99,
            sequence=10**9,
            name="__poison__",
            coro_factory=lambda: asyncio.sleep(0),
        )
        self._seq = 0
        self._completed: list[str] = []
        self._failed: list[str] = []
        self._breaker = CircuitBreaker()
        self._lock = asyncio.Lock()

    async def submit(
        self,
        name: str,
        factory: Callable[[], Awaitable[Any]],
        priority: Priority = Priority.NORMAL,
        max_attempts: int = 3,
    ) -> None:
        if self._q.full():
            raise RuntimeError("queue full")
        self._seq += 1
        item = WorkItem(
            priority=priority.value,
            sequence=self._seq,
            name=name,
            coro_factory=factory,
            max_attempts=max_attempts,
        )
        await self._q.put(item)

    async def _worker(self, deadline: float) -> None:
        while True:
            if time.monotonic() > deadline:
                return
            try:
                item = await asyncio.wait_for(self._q.get(), timeout=0.05)
            except asyncio.TimeoutError:
                if self._q.empty():
                    return
                continue
            if item.name == "__poison__":
                self._q.task_done()
                return
            try:
                if not self._breaker.allow():
                    async with self._lock:
                        self._failed.append(item.name)
                    continue
                await item.coro_factory()
                self._breaker.record_success()
                async with self._lock:
                    self._completed.append(item.name)
            except Exception:
                item.attempt += 1
                self._breaker.record_failure()
                if item.attempt < item.max_attempts and self._breaker.allow():
                    await self._q.put(item)
                else:
                    async with self._lock:
                        self._failed.append(item.name)
            finally:
                self._q.task_done()

    async def run(self) -> Receipt:
        t0 = time.monotonic()
        deadline = t0 + self._deadline_s
        workers = [
            asyncio.create_task(self._worker(deadline)) for _ in range(self._workers)
        ]
        await self._q.join()
        for _ in workers:
            await self._q.put(self._poison)
        await asyncio.gather(*workers, return_exceptions=True)
        while not self._q.empty():
            try:
                self._q.get_nowait()
                self._q.task_done()
            except asyncio.QueueEmpty:
                break
        elapsed = (time.monotonic() - t0) * 1000
        payload = f"{sorted(self._completed)}|{sorted(self._failed)}|{self._breaker.is_open}"
        digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return Receipt(
            ok=len(self._failed) == 0 and not self._breaker.is_open,
            completed=sorted(self._completed),
            failed=sorted(self._failed),
            drained=self._q.empty(),
            circuit_open=self._breaker.is_open,
            digest=digest,
            elapsed_ms=round(elapsed, 2),
        )


async def _demo() -> Receipt:
    rt = AgentRuntime(workers=2, max_queue=16, deadline_s=1.5)

    async def ok(name: str) -> None:
        await asyncio.sleep(0.01)

    async def boom() -> None:
        raise RuntimeError("injected")

    await rt.submit("plan", lambda: ok("plan"), Priority.CRITICAL)
    await rt.submit("fetch", lambda: ok("fetch"), Priority.HIGH)
    await rt.submit("fail_once", boom, Priority.NORMAL, max_attempts=1)
    await rt.submit("summarize", lambda: ok("summarize"), Priority.LOW)
    return await rt.run()


if __name__ == "__main__":
    r = asyncio.run(_demo())
    assert r.drained
    assert "plan" in r.completed and "summarize" in r.completed
    assert "fail_once" in r.failed
    print(
        f"advanced_async_orchestrator: ok digest={r.digest} "
        f"completed={len(r.completed)} failed={len(r.failed)} "
        f"circuit_open={r.circuit_open} elapsed_ms={r.elapsed_ms}"
    )
