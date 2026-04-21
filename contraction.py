# ============================================================
#  STEP D - Belief Base Contraction (Optimized)
# ============================================================

from formulas import Formula, BeliefBase
from resolution import entails

def contract(kb: BeliefBase, alpha: Formula) -> BeliefBase:
    """
    Greedy contraction based on Epistemic Entrenchment.
    Builds the remainder set sequentially prioritizing highest ranks.
    """
    print(f"\n{'='*50}")
    print(f"  Greedy Contraction of KB by: {alpha}")
    print(f"{'='*50}")

    if not entails(kb, alpha):
        print(f"  [Info] KB does not entail {alpha}, returning unchanged base.")
        new_kb = BeliefBase()
        for p, f in kb.beliefs:
            new_kb.add(f, priority=p)
        return new_kb

    surviving_kb = BeliefBase()
    
    for priority, formula in kb.beliefs:
        surviving_kb.add(formula, priority=priority)
        
        if entails(surviving_kb, alpha):
            print(f"  [-] Rejected: {formula} (Priority {priority}) - Causes entailment of {alpha}")
            surviving_kb.remove(formula)
        else:
            print(f"  [+] Kept: {formula} (Priority {priority})")

    print(f"\n  Final remainder set: {[str(f) for f in surviving_kb.get_formulas()]}")
    return surviving_kb

# ============================================================
# DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    from formulas import Atom
    
    print("=" * 55)
    print(" STEP D - Contraction Demonstration")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    kb1 = BeliefBase()
    kb1.add(P >> Q, priority=3)
    kb1.add(Q,      priority=2)
    kb1.add(P,      priority=1)

    print(f"\nInitial KB: {[str(f) for f in kb1.get_formulas()]}")
    new_kb1 = contract(kb1, Q)
    print(f"New KB entails Q? {entails(new_kb1, Q)}")