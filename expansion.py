# ============================================================
#  STEP E - Belief Base Expansion and Revision
# ============================================================

from formulas import Formula, BeliefBase, Not, Atom
from contraction import contract
from resolution import is_consistent

def expand(kb: BeliefBase, alpha: Formula, priority: int = None) -> BeliefBase:
    """
    Blind expansion (KB + α).
    Adds α without checking for logical consistency.

    Priority assignment:
      - If priority is given explicitly, use it.
      - Otherwise, assign max(existing priorities) + 1 so the
        newly accepted belief is the most entrenched in the base.
        This reflects that incoming information is more current
        than what was already believed.
      - If KB is empty, defaults to priority 1.
    """
    new_kb = BeliefBase()
    for p, f in kb.beliefs:
        new_kb.add(f, priority=p)

    if priority is None:
        priority = max((p for p, _ in kb.beliefs), default=0) + 1

    new_kb.add(alpha, priority=priority)
    return new_kb

def revise(kb: BeliefBase, alpha: Formula, priority: int = None) -> BeliefBase:
    """
    Levi Identity revision (KB * α).
    Contracts by ¬α, then expands by α to guarantee consistency.

    The revised belief α receives the highest priority in the result
    (unless overridden), since it is the most recently accepted belief.
    """
    print(f"\n{'='*50}")
    print(f"  REVISION of KB by: {alpha}")
    print(f"{'='*50}")

    negation_alpha = Not(alpha)
    print(f"\n  [Phase 1] Contracting by ¬({alpha}) to clear contradictions...")
    kb_contracted = contract(kb, negation_alpha)

    print(f"\n  [Phase 2] Expanding by {alpha} (highest priority)...")
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

    print(f"\n  KB before: {[(p, str(f)) for p, f in kb1.beliefs]}")
    print(f"  Consistent? {is_consistent(kb1)}")

    kb1_expanded = expand(kb1, Not(P))  # auto priority = 3

    print(f"\n  KB after expansion by ¬P: {[(p, str(f)) for p, f in kb1_expanded.beliefs]}")
    print(f"  Consistent? {is_consistent(kb1_expanded)}")  # False — expected

    print("\n" + "-"*50)
    print("TEST 2 - Revision (Maintains consistency)")
    kb2 = BeliefBase()
    kb2.add(P, priority=2)
    kb2.add(P >> Q, priority=1)

    print(f"\n  KB before: {[(p, str(f)) for p, f in kb2.beliefs]}")
    print(f"  Consistent? {is_consistent(kb2)}")

    kb2_revised = revise(kb2, Not(P))  # auto priority = max(surviving)+1

    print(f"\n  KB after revision by ¬P: {[(p, str(f)) for p, f in kb2_revised.beliefs]}")
    print(f"  Consistent? {is_consistent(kb2_revised)}")  # True — expected

    print("\n" + "-"*50)
    print("TEST 3 - Priority: new belief must have highest priority")
    kb3 = BeliefBase()
    kb3.add(P >> Q, priority=5)
    kb3.add(P, priority=3)

    kb3_revised = revise(kb3, Not(Q))
    print(f"\n  KB after revision by ¬Q: {[(p, str(f)) for p, f in kb3_revised.beliefs]}")
    new_p = next(p for p, f in kb3_revised.beliefs if str(f) == str(Not(Q)))
    max_p = max(p for p, _ in kb3_revised.beliefs)
    print(f"  ¬Q priority: {new_p}, max in base: {max_p}")
    print(f"  New belief has highest priority: {new_p == max_p}")  # True