# Local verification receipts (v1.4)

| Surface | Result |
|---------|--------|
| Tested floors (Python, TS, Rust, Go, C++, Java, Eval, ONNX, Triton, WASM, …) | ok |
| Hardened easy exhibits (Python/Go/Rust) | ok |
| Flagship pipeline | ok |
| MLIR / Coq / Haskell / Zig / Mojo / Elixir / Julia | toolchain_gated (exhibits present, exact blockers) |
| `tower validate` | ok (20 floors) |
| `tower build --all --allow-blocked` | ok |

Formal pair: Lean 4 + Coq. Compiler IR: MLIR attention pipeline sketch.
