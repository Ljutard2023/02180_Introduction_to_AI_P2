# ============================================================
#  AGM POSTULATES TESTS
# ============================================================

from formulas import Atom, BeliefBase, Not, And, Or
from resolution import entails, is_consistent
from expansion import expand, revise

def test_agm_success(kb: BeliefBase, alpha):
    """Success Postulate: α ∈ K * α."""
    revised_kb = revise(kb, alpha)
    success = entails(revised_kb, alpha)
    print(f"  [Success] K * α ⊨ α: {success}")
    assert success, "Success postulate failed."

def test_agm_inclusion(kb: BeliefBase, alpha):
    """Inclusion Postulate: K * α ⊆ K + α."""
    revised_kb = revise(kb, alpha)
    expanded_kb = expand(kb, alpha)
    
    inclusion = True
    for f in revised_kb.get_formulas():
        if not entails(expanded_kb, f):
            inclusion = False
            break
            
    print(f"  [Inclusion] (K * α) ⊆ (K + α): {inclusion}")
    assert inclusion, "Inclusion postulate failed."

def test_agm_vacuity(kb: BeliefBase, alpha):
    """Vacuity Postulate: If ¬α ∉ K, then K * α ≡ K + α."""
    neg_alpha = Not(alpha)
    
    # If KB does not entail ¬α (α is consistent with KB)
    if not entails(kb, neg_alpha):
        revised_kb = revise(kb, alpha)
        expanded_kb = expand(kb, alpha)
        
        # Cross logical equivalence check
        eq1 = all(entails(revised_kb, f) for f in expanded_kb.get_formulas())
        eq2 = all(entails(expanded_kb, f) for f in revised_kb.get_formulas())
        
        vacuity = eq1 and eq2
        print(f"  [Vacuity] K * α ≡ K + α: {vacuity}")
        assert vacuity, "Vacuity postulate failed."
    else:
        print("  [Vacuity] N/A (¬α is entailed by K).")

def test_agm_consistency(kb: BeliefBase, alpha):
    """Consistency Postulate: If α is consistent, K * α is consistent."""
    temp_kb = BeliefBase()
    temp_kb.add(alpha)
    
    if is_consistent(temp_kb):
        revised_kb = revise(kb, alpha)
        consistency = is_consistent(revised_kb)
        print(f"  [Consistency] K * α is consistent: {consistency}")
        assert consistency, "Consistency postulate failed."
    else:
        print("  [Consistency] N/A (α is a contradiction).")

def test_agm_extensionality(kb: BeliefBase, alpha, beta):
    """Extensionality Postulate: If α ≡ β, then K * α ≡ K * β."""
    temp_kb_a = BeliefBase()
    temp_kb_a.add(alpha)
    temp_kb_b = BeliefBase()
    temp_kb_b.add(beta)
    
    if entails(temp_kb_a, beta) and entails(temp_kb_b, alpha):
        revised_a = revise(kb, alpha)
        revised_b = revise(kb, beta)
        
        # Cross logical equivalence check
        eq1 = all(entails(revised_a, f) for f in revised_b.get_formulas())
        eq2 = all(entails(revised_b, f) for f in revised_a.get_formulas())
        
        extensionality = eq1 and eq2
        print(f"  [Extensionality] K * α ≡ K * β: {extensionality}")
        assert extensionality, "Extensionality postulate failed."
    else:
        print("  [Extensionality] N/A (α is not equivalent to β).")

# ============================================================
#  TEST EXECUTION
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print(" AGM POSTULATES VERIFICATION")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")

    kb = BeliefBase()
    kb.add(P >> Q, priority=2)
    kb.add(P, priority=1)

    print("\n--- Test with α = ¬Q ---")
    alpha = Not(Q)
    
    test_agm_success(kb, alpha)
    test_agm_inclusion(kb, alpha)
    test_agm_vacuity(kb, alpha)
    test_agm_consistency(kb, alpha)
    
    print("\n--- Extensionality Test with α = ¬(P ∧ Q) and β = ¬P ∨ ¬Q ---")
    alpha_ext = Not(And(P, Q))
    beta_ext = Or(Not(P), Not(Q))
    test_agm_extensionality(kb, alpha_ext, beta_ext)