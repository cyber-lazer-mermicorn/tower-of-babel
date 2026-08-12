#!/usr/bin/env python3
"""Advanced exhibit: drainable priority agent runtime.

Owns a real boundary: bounded queues, FIFO ties, futures, retries,
graceful shutdown, and a structured receipt. No placeholders.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Optional


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
    duration_ms: float
    digest: str


class AsyncOrchestrator:
    """Bounded priority work queue with isolation and receipt."""

    def __init__(self, max_concurrent: int = 4, queue_size: int = 64):
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be >= 1")
        self._max_concurrent = max_concurrent
        self._queue: asyncio.PriorityQueue[WorkItem] = asyncio.PriorityQueue(maxsize=queue_size)
        self._seq = 0
        self._completed: list[str] = []
        self._failed: list[str] = []
        self._shutdown = asyncio.Event()
        self._workers: list[asyncio.Task] = []

    def submit(
        self,
        name: str,
        coro_factory: Callable[[], Awaitable[Any]],
        priority: Priority = Priority.NORMAL,
        max_attempts: int = 3,
    ) -> None:
        if self._shutdown.is_set():
            raise RuntimeError("orchestrator is shutting down")
        self._seq += 1
        item = WorkItem(
            priority=priority.value,
            sequence=self._seq,
            name=name,
            coro_factory=coro_factory,
            max_attempts=max_attempts,
        )
        try:
            self._queue.put_nowait(item)
        except asyncio.QueueFull as e:
            raise RuntimeError(f"queue full; cannot accept {name}") from e

    async def _worker(self) -> None:
        while not self._shutdown.is_set() or not self._queue.empty():
            try:
                item = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                if self._shutdown.is_set():
                    break
                continue
            item.attempt += 1
            try:
                await item.coro_factory()
                self._completed.append(item.name)
            except Exception:
                if item.attempt < item.max_attempts:
                    # re-queue with same priority, later sequence
                    self._seq += 1
                    item.sequence = self._seq
                    await self._queue.put(item)
                else:
                    self._failed.append(item.name)
            finally:
                self._queue.task_done()

    async def run(self, drain: bool = True) -> Receipt:
        start = time.perf_counter()
        self._workers = [
            asyncio.create_task(self._worker()) for _ in range(self._max_concurrent)
        ]
        if drain:
            await self._queue.join()
            self._shutdown.set()
        await asyncio.gather(*self._workers, return_exceptions=True)
        duration_ms = (time.perf_counter() - start) * 1000
        payload = f"{sorted(self._completed)}|{sorted(self._failed)}|{drain}"
        digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return Receipt(
            ok=len(self._failed) == 0,
            completed=list(self._completed),
            failed=list(self._failed),
            drained=drain,
            duration_ms=round(duration_ms, 2),
            digest=digest,
        )

    async def shutdown(self) -> None:
        self._shutdown.set()


async def _demo() -> None:
    orch = AsyncOrchestrator(max_concurrent=2, queue_size=16)

    async def ok_task(name: str, delay: float = 0.01):
        await asyncio.sleep(delay)
        return name

    async def fail_once():
        if not hasattr(fail_once, "_hit"):
            fail_once._hit = True  # type: ignore
            raise RuntimeError("transient")
        return "recovered"

    orch.submit("alpha", lambda: ok_task("alpha"), Priority.HIGH)
    orch.submit("beta", lambda: ok_task("beta"), Priority.NORMAL)
    orch.submit("gamma", fail_once, Priority.CRITICAL, max_attempts=2)

    receipt = await orch.run(drain=True)
    assert receipt.ok, receipt
    assert "gamma" in receipt.completed
    print(f"advanced_async_orchestrator: ok digest={receipt.digest}")


if __name__ == "__main__":
    asyncio.run(_demo())
