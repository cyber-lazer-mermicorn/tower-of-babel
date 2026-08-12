#!/usr/bin/env python3
"""Easy exhibit: single metric score. Teaches the evaluation idea only."""

def accuracy(y_true: list[int], y_pred: list[int]) -> float:
    if not y_true:
        raise ValueError("y_true must be non-empty")
    if len(y_true) != len(y_pred):
        raise ValueError("length mismatch")
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    return correct / len(y_true)


if __name__ == "__main__":
    assert accuracy([1, 0, 1], [1, 0, 0]) == 2 / 3
    print("easy_score: ok")
