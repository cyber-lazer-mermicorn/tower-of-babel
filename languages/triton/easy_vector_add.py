#!/usr/bin/env python3
"""Easy exhibit: elementwise add. Teaches the kernel idea only (host Python)."""

def vector_add(a: list[float], b: list[float]) -> list[float]:
    if len(a) != len(b):
        raise ValueError("length mismatch")
    return [x + y for x, y in zip(a, b)]


if __name__ == "__main__":
    assert vector_add([1.0, 2.0], [3.0, 4.0]) == [4.0, 6.0]
    print("easy_vector_add: ok")
