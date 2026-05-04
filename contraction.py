#  Step D - Belief Base Contraction

from formulas import Formula, BeliefBase
from resolution import entails

def contract(kb: BeliefBase, alpha: Formula, verbose: bool = True) -> BeliefBase:
    """
    Greedy contraction based on Epistemic Entrenchment.
    Builds the remainder set sequentially prioritizing highest ranks.
    Set verbose=False to suppress all internal print output.
    """
    if verbose:
        print(f"\n{'='*50}")
        print(f"  Greedy Contraction of KB by: {alpha}")
        print(f"{'='*50}")

    if not entails(kb, alpha):
        if verbose:
            print(f"  [Info] KB does not entail {alpha}, returning unchanged base.")
        new_kb = BeliefBase()
        for p, f in kb.beliefs:
            new_kb.add(f, priority=p, verbose=False)
        return new_kb

    surviving_kb = BeliefBase()

    for priority, formula in kb.beliefs:
        surviving_kb.add(formula, priority=priority, verbose=False)

        if entails(surviving_kb, alpha):
            if verbose:
                print(f"  [-] Rejected: {formula} (Priority {priority}) - Causes entailment of {alpha}")
            surviving_kb.remove(formula, verbose=False)
        else:
            if verbose:
                print(f"  [+] Kept: {formula} (Priority {priority})")

    if verbose:
        print(f"\n  Final remainder set: {[str(f) for f in surviving_kb.get_formulas()]}")
    return surviving_kb

# Demonstration

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
    new_kb1 = contract(kb1, Q, verbose=True)
    print(f"New KB entails Q? {entails(new_kb1, Q)}")