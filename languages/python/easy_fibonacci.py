#!/usr/bin/env python3
"""Easy exhibit: pure iterative Fibonacci.

Teaches the core idea only. No production claims.
"""

def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


if __name__ == "__main__":
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55
    print("easy_fibonacci: ok")
