# ============================================================
#  STEP E - Belief Base Expansion and Revision
# ============================================================

from formulas import Formula, BeliefBase, Not, Atom
from contraction import contract
from resolution import is_consistent

def expand(kb: BeliefBase, alpha: Formula, priority: int = 1) -> BeliefBase:
    """
    Blind expansion (KB + α). 
    Adds α without checking for logical consistency.
    """
    new_kb = BeliefBase()
    for p, f in kb.beliefs:
        new_kb.add(f, priority=p)
        
    new_kb.add(alpha, priority=priority)
    return new_kb

def revise(kb: BeliefBase, alpha: Formula, priority: int = 1) -> BeliefBase:
    """
    Levi Identity revision (KB * α).
    Contracts by ¬α, then expands by α to guarantee consistency.
    """
    print(f"\n{'='*50}")
    print(f"  REVISION of KB by: {alpha}")
    print(f"{'='*50}")

    negation_alpha = Not(alpha)
    print(f"\n  [Phase 1] Contracting by ¬({alpha}) to clear contradictions...")
    kb_contracted = contract(kb, negation_alpha)

    print(f"\n  [Phase 2] Expanding by {alpha}...")
    new_kb = expand(kb_contracted, alpha, priority)

    return new_kb

# ============================================================
# DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print(" STEP E - Expansion and Revision Demonstration")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")

    print("\n" + "-"*50)
    print("TEST 1 - Expansion (Creates contradiction)")
    kb1 = BeliefBase()
    kb1.add(P, priority=2)
    
    print(f"\n  KB before: {[str(f) for f in kb1.get_formulas()]}")
    print(f"  Consistent? {is_consistent(kb1)}")
    
    kb1_expanded = expand(kb1, Not(P), priority=3)
    
    print(f"\n  KB after expansion by ¬P: {[str(f) for f in kb1_expanded.get_formulas()]}")
    print(f"  Consistent? {is_consistent(kb1_expanded)}")

    print("\n" + "-"*50)
    print("TEST 2 - Revision (Maintains consistency)")
    kb2 = BeliefBase()
    kb2.add(P, priority=2)
    kb2.add(P >> Q, priority=1)
    
    print(f"\n  KB before: {[str(f) for f in kb2.get_formulas()]}")
    print(f"  Consistent? {is_consistent(kb2)}")
    
    kb2_revised = revise(kb2, Not(P), priority=3)
    
    print(f"\n  KB after revision by ¬P: {[str(f) for f in kb2_revised.get_formulas()]}")
    print(f"  Consistent? {is_consistent(kb2_revised)}")