# ============================================================
#  CONTRACTION  (Partial Meet Contraction)
# ============================================================
#
#  Contraction: KB ÷ α
#  Goal: remove α from what KB believes, with minimal loss,
#        respecting the priority order on beliefs.
#
#  Algorithm (full partial meet, three steps):
#
#  Step 1 — Remainder sets (KB perp alpha):
#    Find every MAXIMAL subset S of KB such that S ⊭ α.
#    "Maximal" means: adding any belief back would make S entail α again.
#
#  Step 2 — Selection function γ:
#    Score each remainder set by the SUM of priorities of its beliefs.
#    Keep only the highest-scoring remainder sets.
#    This implements "epistemic entrenchment": high-priority beliefs
#    are retained whenever possible.
#
#  Step 3 — Intersection:
#    The contracted KB is the intersection of all selected remainder sets.
#    Beliefs that survive in ALL selected remainders are kept.
#
#  Special cases:
#    - If KB ⊭ α already → return KB unchanged (Vacuity).
#    - If α is a tautology → return empty KB (cannot remove a tautology
#      by removing beliefs; the only consistent option is empty base).

from formulas import BeliefBase, Formula, Not
from resolution import entails, is_consistent


# ============================================================
#  STEP 1 — REMAINDER SETS
# ============================================================

def remainder_sets(kb: BeliefBase, alpha: Formula) -> list:
    """Computes all maximal subsets of KB that do not entail alpha.

    A remainder set S ∈ (KB perp alpha) satisfies:
      1. S ⊆ KB
      2. S ⊭ α
      3. For every f ∈ KB \ S:  S ∪ {f} ⊨ α  (maximality)

    We generate all subsets of KB and filter, then keep only maximal ones.
    This is tractable for the small belief bases used in this assignment.
    For large KBs a smarter search would be needed.
    """
    beliefs = kb.beliefs  # list of (priority, formula)
    n = len(beliefs)
    candidates = []

    # Enumerate all 2^n subsets
    for mask in range(2 ** n):
        subset = [beliefs[i] for i in range(n) if (mask >> i) & 1]

        # Build a temporary KB from this subset
        temp_kb = BeliefBase()
        for priority, formula in subset:
            temp_kb.beliefs.append((priority, formula))

        # Keep only subsets that do NOT entail alpha
        if not entails(temp_kb, alpha):
            candidates.append(subset)

    # Keep only MAXIMAL candidates:
    # A candidate is maximal if no other candidate is a strict superset of it.
    maximal = []
    for candidate in candidates:
        candidate_formulas = {f for (_, f) in candidate}
        dominated = False
        for other in candidates:
            if candidate is other:
                continue
            other_formulas = {f for (_, f) in other}
            # 'other' strictly contains 'candidate'
            if candidate_formulas < other_formulas:
                dominated = True
                break
        if not dominated:
            maximal.append(candidate)

    return maximal


# ============================================================
#  STEP 2 — SELECTION FUNCTION
# ============================================================

def select(remainders: list) -> list:
    """Selects the best remainder sets based on total priority score.

    The selection function implements epistemic entrenchment:
    we prefer remainder sets that retain high-priority beliefs.

    Score = sum of priorities of all beliefs in the remainder set.
    Returns all remainder sets that achieve the maximum score.
    """
    if not remainders:
        return []

    # Score each remainder set
    scored = [(sum(p for p, _ in r), r) for r in remainders]
    max_score = max(score for score, _ in scored)

    # Return all remainder sets tied at the maximum score
    return [r for score, r in scored if score == max_score]


# ============================================================
#  STEP 3 — INTERSECTION
# ============================================================

def intersect(selected: list) -> list:
    """Returns beliefs that appear in ALL selected remainder sets.

    A belief (priority, formula) survives contraction only if it is
    present in every selected remainder set — this is the 'meet' in
    partial meet contraction.
    """
    if not selected:
        return []

    # Convert each remainder set to a set of formulas for intersection
    formula_sets = [frozenset(f for _, f in r) for r in selected]

    # Intersection: formulas common to all selected remainders
    common_formulas = formula_sets[0]
    for fs in formula_sets[1:]:
        common_formulas = common_formulas & fs

    # Rebuild (priority, formula) pairs from the first remainder set
    # (priorities are consistent across remainder sets — same original KB)
    priority_map = {}
    for r in selected:
        for p, f in r:
            priority_map[f] = p

    return [(priority_map[f], f) for f in common_formulas]


# ============================================================
#  PUBLIC API
# ============================================================

def contract(kb: BeliefBase, alpha: Formula) -> BeliefBase:
    """Performs partial meet contraction: KB ÷ α.

    Returns a new BeliefBase. The original KB is not modified.

    Special cases handled:
      - KB ⊭ α  →  return KB unchanged (Vacuity postulate)
      - α is tautology  →  return empty KB (cannot remove a tautology)
      - KB is empty  →  return empty KB
    """
    result = BeliefBase()

    # Vacuity: if KB doesn't even entail alpha, nothing to contract
    if not entails(kb, alpha):
        print(f"  [Contraction] KB ⊭ {alpha} — returning KB unchanged (Vacuity).")
        for priority, formula in kb.beliefs:
            result.beliefs.append((priority, formula))
        return result

    # Empty KB: nothing to remove
    if kb.is_empty():
        print(f"  [Contraction] KB is empty — nothing to contract.")
        return result

    print(f"  [Contraction] Computing KB ÷ {alpha}...")

    # Step 1: find all maximal non-entailing subsets
    remainders = remainder_sets(kb, alpha)

    if not remainders:
        # Every subset entails alpha — only possible if alpha is a tautology.
        # The contracted KB must be empty.
        print(f"  [Contraction] No remainder sets found — α may be a tautology. Returning empty KB.")
        return result

    # Step 2: select best remainder sets by priority score
    selected = select(remainders)

    # Step 3: intersect selected remainder sets
    surviving = intersect(selected)

    # Build the result KB, preserving original sort order (high priority first)
    surviving.sort(key=lambda x: x[0], reverse=True)
    for priority, formula in surviving:
        result.beliefs.append((priority, formula))

    print(f"  [Contraction] Done. Removed beliefs that caused entailment of {alpha}.")
    return result


# ============================================================
#  DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    from formulas import Atom, Not, And, Or

    print("=" * 55)
    print(" CONTRACTION - Partial Meet Demonstration")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    # ── Test 1: Basic contraction ────────────────────────────
    # KB = {P→Q (p=2), P (p=1)}  entails Q
    # After KB ÷ Q, KB should no longer entail Q
    print("\n── Test 1: Basic contraction ──")
    kb1 = BeliefBase()
    kb1.add(P >> Q, priority=2)
    kb1.add(P, priority=1)

    print(f"Before: {kb1}")
    print(f"  KB ⊨ Q: {entails(kb1, Q)}")

    kb1_contracted = contract(kb1, Q)
    print(f"After KB ÷ Q: {kb1_contracted}")
    print(f"  KB ÷ Q ⊨ Q: {entails(kb1_contracted, Q)}")  # Should be False

    # ── Test 2: Priority respected ───────────────────────────
    # KB = {P (p=3), P→Q (p=1)}  entails Q
    # High-priority P should be kept; P→Q should be dropped
    print("\n── Test 2: Priority respected ──")
    kb2 = BeliefBase()
    kb2.add(P, priority=3)
    kb2.add(P >> Q, priority=1)

    print(f"Before: {kb2}")
    kb2_contracted = contract(kb2, Q)
    print(f"After KB ÷ Q: {kb2_contracted}")
    print(f"  Still contains P: {any(str(f) == 'P' for _, f in kb2_contracted.beliefs)}")       # True
    print(f"  Still contains P→Q: {any(str(f) == '(P → Q)' for _, f in kb2_contracted.beliefs)}")  # False

    # ── Test 3: Vacuity — alpha not entailed ─────────────────
    # KB = {P}  does not entail Q
    # KB ÷ Q should return KB unchanged
    print("\n── Test 3: Vacuity ──")
    kb3 = BeliefBase()
    kb3.add(P, priority=1)

    print(f"Before: {kb3}")
    kb3_contracted = contract(kb3, Q)
    print(f"After KB ÷ Q: {kb3_contracted}")  # Should still contain P

    # ── Test 4: Joint entailment ─────────────────────────────
    # KB = {P (p=2), Q (p=2), P∧Q→R (p=1)}  entails R
    # Neither P nor Q alone causes entailment — the conjunction does
    # Partial meet should remove P∧Q→R (lowest priority)
    print("\n── Test 4: Joint entailment ──")
    kb4 = BeliefBase()
    kb4.add(P, priority=2)
    kb4.add(Q, priority=2)
    kb4.add((P & Q) >> R, priority=1)

    print(f"Before: {kb4}")
    print(f"  KB ⊨ R: {entails(kb4, R)}")

    kb4_contracted = contract(kb4, R)
    print(f"After KB ÷ R: {kb4_contracted}")
    print(f"  KB ÷ R ⊨ R: {entails(kb4_contracted, R)}")  # Should be False
