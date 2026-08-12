#!/usr/bin/env python3
"""Easy exhibit: pure-Python linear model shape. No ONNX runtime required."""

def linear_predict(weights: list[float], bias: float, x: list[float]) -> float:
    if len(weights) != len(x):
        raise ValueError("dimension mismatch")
    return sum(w * v for w, v in zip(weights, x)) + bias


if __name__ == "__main__":
    y = linear_predict([0.5, -1.0], 0.1, [2.0, 1.0])
    assert abs(y - 0.1) < 1e-9
    print("easy_linear_model: ok")
