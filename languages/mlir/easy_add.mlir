// Easy exhibit: scalar add in MLIR arithmetic dialect.
// Teaches IR shape only. Toolchain_gated without mlir-opt.
module {
  func.func @add(%a: f32, %b: f32) -> f32 {
    %c = arith.addf %a, %b : f32
    return %c : f32
  }
}
