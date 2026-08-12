-- Advanced exhibit: monotone authority / receipt ordering sketch.
-- Kernel-checked properties for a simple gate.

namespace Tower

inductive Verdict where
  | allow
  | block
deriving DecidableEq, Repr

structure Decision where
  verdict : Verdict
  step    : Nat
deriving Repr

/-- A sequence is monotone in step numbers. --/
def monotone (ds : List Decision) : Prop :=
  match ds with
  | [] | [_] => True
  | d1 :: d2 :: rest => d1.step ≤ d2.step ∧ monotone (d2 :: rest)

theorem monotone_nil : monotone [] := trivial

theorem monotone_singleton (d : Decision) : monotone [d] := trivial

/-- Once blocked, we treat further allows as a policy violation in this model. --/
def no_allow_after_block : List Decision → Prop
  | [] => True
  | Decision.mk Verdict.block _ :: rest =>
      rest.all (fun d => d.verdict = Verdict.block)
  | _ :: rest => no_allow_after_block rest

end Tower
