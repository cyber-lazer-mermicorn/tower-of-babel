# Local verification receipts (v1.3)

| Surface | Result |
|---------|--------|
| Prior tested floors (Python, TS, Rust, Go, C++, Java, Eval, ONNX, Triton, …) | ok |
| Flagship pipeline | ok |
| Haskell / Zig / Mojo / Elixir | toolchain_gated (exact blocker — exhibits present) |
| `tower validate` | ok (18 floors) |
| `tower build --all --allow-blocked` | ok |

Gated floors ship complete exhibits and claim only what the environment can prove.
