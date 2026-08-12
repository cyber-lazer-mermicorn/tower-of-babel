(* Advanced exhibit: linked receipt-chain ordering.
   Owns formal boundary complementary to Lean 4:
   constructive chain-step and ordered-list invariants.
   Toolchain_gated without coqc. *)

Require Import List.
Import ListNotations.

Record Receipt := mkReceipt {
  rid : nat;
  step : nat;
  digest : nat
}.

Inductive ordered : list Receipt -> Prop :=
| ordered_nil : ordered []
| ordered_one : forall r, ordered [r]
| ordered_cons : forall r1 r2 rest,
    step r1 <= step r2 ->
    ordered (r2 :: rest) ->
    ordered (r1 :: r2 :: rest).

Definition append_receipt (chain : list Receipt) (r : Receipt) : list Receipt :=
  chain ++ [r].

Lemma ordered_singleton : forall r, ordered [r].
Proof. intros. apply ordered_one. Qed.

Lemma ordered_extend_tip :
  forall tip rest r,
    ordered (tip :: rest) ->
    step tip <= step r ->
    ordered (tip :: rest ++ [r]).
Proof.
  intros tip rest r Hord Hle.
  induction rest as [|t rest' IH].
  - apply ordered_cons; [exact Hle | apply ordered_one].
  - inversion Hord; subst.
    apply ordered_cons; [assumption|].
    apply IH; assumption.
Qed.

Fixpoint max_step (xs : list Receipt) : nat :=
  match xs with
  | [] => 0
  | r :: rs => Nat.max (step r) (max_step rs)
  end.

Theorem ordered_nil_ok : ordered [].
Proof. apply ordered_nil. Qed.

Definition receipt_chain_invariant (xs : list Receipt) : Prop := ordered xs.
