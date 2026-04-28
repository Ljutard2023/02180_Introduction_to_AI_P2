# ============================================================
#  AGM POSTULATES TESTS
# ============================================================

from formulas import Atom, BeliefBase, Not, And, Or
from resolution import entails, is_consistent
from expansion import expand, revise
from contraction import contract

def test_agm_success(kb: BeliefBase, alpha):
    """Success Postulate: α ∈ K * α."""
    revised_kb = revise(kb, alpha, verbose=False)
    success = entails(revised_kb, alpha)
    print(f"  [Success] K * α ⊨ α: {success}")
    assert success, "Success postulate failed."

def test_agm_inclusion(kb: BeliefBase, alpha):
    """Inclusion Postulate: K * α ⊆ K + α."""
    revised_kb = revise(kb, alpha, verbose=False)
    expanded_kb = expand(kb, alpha, verbose=False)
    
    inclusion = True
    for f in revised_kb.get_formulas():
        if not entails(expanded_kb, f):
            inclusion = False
            break
            
    print(f"  [Inclusion] (K * α) ⊆ (K + α): {inclusion}")
    assert inclusion, "Inclusion postulate failed."

def test_agm_vacuity(kb: BeliefBase, alpha):
    """Vacuity Postulate: If ¬α ∉ K, then K * α ≡ K + α.

    This postulate only fires when KB does NOT entail ¬α.
    It verifies that revision is identical to simple expansion
    when there is no conflict to resolve.
    """
    neg_alpha = Not(alpha)
    
    if not entails(kb, neg_alpha):
        revised_kb = revise(kb, alpha, verbose=False)
        expanded_kb = expand(kb, alpha, verbose=False)
        
        eq1 = all(entails(revised_kb, f) for f in expanded_kb.get_formulas())
        eq2 = all(entails(expanded_kb, f) for f in revised_kb.get_formulas())
        
        vacuity = eq1 and eq2
        print(f"  [Vacuity] K * α ≡ K + α: {vacuity}")
        assert vacuity, "Vacuity postulate failed."
    else:
        print("  [Vacuity] N/A (¬α is entailed by K — use a non-conflicting KB to exercise this).")

def test_agm_consistency(kb: BeliefBase, alpha):
    """Consistency Postulate: If α is consistent, K * α is consistent."""
    temp_kb = BeliefBase()
    temp_kb.add(alpha, verbose=False)
    
    if is_consistent(temp_kb):
        revised_kb = revise(kb, alpha, verbose=False)
        consistency = is_consistent(revised_kb)
        print(f"  [Consistency] K * α is consistent: {consistency}")
        assert consistency, "Consistency postulate failed."
    else:
        print("  [Consistency] N/A (α is a contradiction).")

def test_agm_extensionality(kb: BeliefBase, alpha, beta):
    """Extensionality Postulate: If α ≡ β, then K * α ≡ K * β."""
    temp_kb_a = BeliefBase()
    temp_kb_a.add(alpha, verbose=False)
    temp_kb_b = BeliefBase()
    temp_kb_b.add(beta, verbose=False)
    
    if entails(temp_kb_a, beta) and entails(temp_kb_b, alpha):
        revised_a = revise(kb, alpha, verbose=False)
        revised_b = revise(kb, beta, verbose=False)
        
        eq1 = all(entails(revised_a, f) for f in revised_b.get_formulas())
        eq2 = all(entails(revised_b, f) for f in revised_a.get_formulas())
        
        extensionality = eq1 and eq2
        print(f"  [Extensionality] K * α ≡ K * β: {extensionality}")
        assert extensionality, "Extensionality postulate failed."
    else:
        print("  [Extensionality] N/A (α is not equivalent to β).")

def test_contraction_success(kb: BeliefBase, alpha):
    """Contraction Success: KB ÷ α should no longer entail α."""
    contracted = contract(kb, alpha, verbose=False)
    success = not entails(contracted, alpha)
    print(f"  [Contraction Success] KB÷α ⊭ α: {success}")
    assert success, "Contraction success postulate failed."

def test_contraction_inclusion(kb: BeliefBase, alpha):
    """Contraction Inclusion: KB ÷ α ⊆ KB (no beliefs are added)."""
    contracted = contract(kb, alpha, verbose=False)
    inclusion = all(entails(kb, f) for f in contracted.get_formulas())
    print(f"  [Contraction Inclusion] KB÷α ⊆ KB: {inclusion}")
    assert inclusion, "Contraction inclusion postulate failed."

def test_contraction_vacuity(kb: BeliefBase, alpha):
    """Contraction Vacuity: If KB ⊭ α, then KB ÷ α = KB."""
    if not entails(kb, alpha):
        contracted = contract(kb, alpha, verbose=False)
        eq1 = all(entails(kb, f) for f in contracted.get_formulas())
        eq2 = all(entails(contracted, f) for f in kb.get_formulas())
        vacuity = eq1 and eq2
        print(f"  [Contraction Vacuity] KB÷α = KB: {vacuity}")
        assert vacuity, "Contraction vacuity postulate failed."
    else:
        print("  [Contraction Vacuity] N/A (KB already entails α).")

# ============================================================
#  TEST EXECUTION
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print(" AGM POSTULATES VERIFICATION")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    # ── Scenario 1: Conflicting revision ────────────────────
    # KB entails Q (via P and P→Q), alpha=¬Q creates conflict.
    # Vacuity prints N/A here — that is correct behaviour.
    print("\n--- Scenario 1: KB={P→Q, P}, α=¬Q (conflicting revision) ---")
    kb1 = BeliefBase()
    kb1.add(P >> Q, priority=2, verbose=False)
    kb1.add(P, priority=1, verbose=False)
    alpha = Not(Q)

    test_agm_success(kb1, alpha)
    test_agm_inclusion(kb1, alpha)
    test_agm_vacuity(kb1, alpha)       # N/A — KB entails Q = ¬(¬Q)
    test_agm_consistency(kb1, alpha)

    # ── Scenario 2: Non-conflicting revision ─────────────────
    # KB={R} does not entail ¬P, so revising with P is vacuous:
    # K*P should equal K+P (no contraction needed).
    print("\n--- Scenario 2: KB={R}, α=P (non-conflicting — Vacuity fires) ---")
    kb2 = BeliefBase()
    kb2.add(R, priority=1, verbose=False)

    test_agm_vacuity(kb2, P)           # Fires: K*P ≡ K+P

    # ── Scenario 3: Extensionality ───────────────────────────
    # ¬(P∧Q) ≡ ¬P∨¬Q ≡ P→¬Q — all three are equivalent.
    print("\n--- Scenario 3: Extensionality — α=¬(P∧Q), β=P→¬Q ---")
    alpha_ext = Not(And(P, Q))
    beta_ext  = P >> Not(Q)
    test_agm_extensionality(kb1, alpha_ext, beta_ext)

    # ── Scenario 4: Contraction postulates ───────────────────
    print("\n--- Scenario 4: Contraction postulates ---")
    kb3 = BeliefBase()
    kb3.add(P >> Q, priority=2, verbose=False)
    kb3.add(P, priority=1, verbose=False)

    test_contraction_success(kb3, Q)    # KB÷Q should not entail Q
    test_contraction_inclusion(kb3, Q)  # KB÷Q ⊆ KB
    test_contraction_vacuity(kb3, R)    # KB doesn't entail R → KB÷R = KB