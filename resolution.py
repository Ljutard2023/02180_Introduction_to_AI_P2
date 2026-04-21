# ============================================================
#  RESOLUTION-BASED ENTAILMENT
# ============================================================
#
#  Core idea (from lecture 10):
#    KB |= α   iff   KB ∧ ¬α  is unsatisfiable
#
#  We prove unsatisfiability by:
#    1. Converting all formulas (KB + ¬α) to CNF clause sets.
#    2. Repeatedly applying the resolution rule on pairs of clauses
#       that contain complementary literals (P and ¬P).
#    3. If we ever derive the empty clause {} → KB entails α.
#       If no new clauses can be added → KB does NOT entail α.

from formulas import Atom, Not, And, Or, Implies, BeliefBase, Formula
from cnf import to_cnf


# ============================================================
#  LITERAL HELPERS
# ============================================================

def negate_literal(literal) -> Formula:
    """Returns the complement of a literal.
       ¬(¬P) = P,   ¬P → ¬P (already negated atom stays as Not).
    """
    if isinstance(literal, Not):
        return literal.formula   # ¬(¬P) → P
    elif isinstance(literal, Atom):
        return Not(literal)      # P     → ¬P
    else:
        raise ValueError(f"Expected a literal, got: {literal}")


def literal_name(literal) -> str:
    """Canonical string key for a literal, used to detect complements.
       Both P and ¬P map to the atom name 'P' so we can pair them.
    """
    if isinstance(literal, Atom):
        return literal.name
    elif isinstance(literal, Not) and isinstance(literal.formula, Atom):
        return literal.formula.name
    else:
        raise ValueError(f"Not a flat literal: {literal}")


def is_positive(literal) -> bool:
    """True if the literal is a plain Atom (positive), False if Not(Atom)."""
    return isinstance(literal, Atom)


# ============================================================
#  THE RESOLUTION RULE
# ============================================================

def resolve(clause_a: frozenset, clause_b: frozenset) -> list:
    """Applies the resolution rule to two clauses.

    For each literal L in clause_a, if ¬L is in clause_b,
    produce the resolvent: (clause_a - {L}) ∪ (clause_b - {¬L}).

    Returns a list of all possible resolvents (usually 0 or 1).
    If a resolvent is a tautology (contains both P and ¬P), discard it —
    tautological clauses add no information.
    """
    resolvents = []

    for lit in clause_a:
        complement = negate_literal(lit)

        # Check if the complement actually appears in clause_b
        if complement in clause_b:
            # Build the resolvent by removing the resolved pair
            new_clause = (clause_a - {lit}) | (clause_b - {complement})

            # Discard tautological resolvents (e.g., {P, ¬P, Q})
            if not is_tautological(new_clause):
                resolvents.append(frozenset(new_clause))

    return resolvents


def is_tautological(clause: frozenset) -> bool:
    """Returns True if a clause contains both P and ¬P for any atom P.
       Such a clause is always true and useless.
    """
    for lit in clause:
        if isinstance(lit, Atom) and Not(lit) in clause:
            return True
        if isinstance(lit, Not) and isinstance(lit.formula, Atom) and lit.formula in clause:
            return True
    return False


# ============================================================
#  MAIN RESOLUTION LOOP
# ============================================================

def pl_resolution(clauses: set) -> bool:
    """Runs the resolution closure algorithm on a set of CNF clauses.

    Returns True  if the empty clause is derived (set is unsatisfiable).
    Returns False if no new clauses can be generated (set is satisfiable).
    """
    # Work with a mutable copy; track all known clauses to avoid re-processing
    known = set(clauses)
    # The frontier is every pair we still need to try resolving
    # We use a worklist: start with everything, add new clauses as we go
    new_clauses = set()

    while True:
        clause_list = list(known)
        n = len(clause_list)
        generated_something = False

        for i in range(n):
            for j in range(i + 1, n):
                resolvents = resolve(clause_list[i], clause_list[j])

                for resolvent in resolvents:
                    # Empty clause = contradiction found → unsatisfiable
                    if len(resolvent) == 0:
                        return True  # KB ∧ ¬α is unsatisfiable → KB |= α

                    if resolvent not in known:
                        new_clauses.add(resolvent)
                        generated_something = True

        if not generated_something:
            # Saturated: no new clauses possible → satisfiable → KB ⊭ α
            return False

        known |= new_clauses
        new_clauses = set()


# ============================================================
#  PUBLIC API
# ============================================================

def entails(kb: BeliefBase, alpha: Formula) -> bool:
    """Returns True if the belief base KB logically entails formula α.

    Method: KB |= α  iff  KB ∧ ¬α is unsatisfiable (proof by refutation).
    Steps:
      1. Convert each formula in KB to CNF clauses.
      2. Convert ¬α to CNF clauses.
      3. Run resolution on the combined clause set.
    """
    all_clauses = set()

    # Step 1: Add CNF of every belief in KB
    for formula in kb.get_formulas():
        all_clauses |= to_cnf(formula)

    # Step 2: Add CNF of ¬α (the negation of what we want to prove)
    negated_alpha = Not(alpha)
    all_clauses |= to_cnf(negated_alpha)

    # Step 3: Resolution — returns True if empty clause is derived
    return pl_resolution(all_clauses)


def is_consistent(kb: BeliefBase) -> bool:
    """Returns True if the belief base KB is logically consistent
    (i.e., does not entail a contradiction).

    A KB is inconsistent iff it entails False, which we detect by
    running resolution on the KB's CNF clauses alone (no added negation).
    If the empty clause is derivable from KB itself → inconsistent.
    """
    all_clauses = set()
    for formula in kb.get_formulas():
        all_clauses |= to_cnf(formula)

    return not pl_resolution(all_clauses)


# ============================================================
#  DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    from formulas import Atom, BeliefBase, Not, And, Or

    print("=" * 55)
    print(" RESOLUTION - Entailment Demonstration")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    # --- Basic modus ponens: {P→Q, P} |= Q ---
    kb1 = BeliefBase()
    kb1.add(P >> Q, priority=2)
    kb1.add(P, priority=1)

    print(f"\nKB1: {kb1}")
    print(f"  KB1 |= Q           : {entails(kb1, Q)}")          # True
    print(f"  KB1 |= P           : {entails(kb1, P)}")          # True
    print(f"  KB1 |= ¬Q          : {entails(kb1, Not(Q))}")     # False
    print(f"  KB1 |= P ∨ R       : {entails(kb1, P | R)}")      # True
    print(f"  KB1 consistent    : {is_consistent(kb1)}")        # True

    # --- Inconsistent KB: {P, ¬P} ---
    kb2 = BeliefBase()
    kb2.add(P, priority=1)
    kb2.add(Not(P), priority=1)

    print(f"\nKB2: {kb2}")
    print(f"  KB2 consistent    : {is_consistent(kb2)}")        # False
    print(f"  KB2 |= Q           : {entails(kb2, Q)}")          # True (ex falso)

    # --- Chained implication: {P→Q, Q→R, P} |= R ---
    kb3 = BeliefBase()
    kb3.add(P >> Q, priority=3)
    kb3.add(Q >> R, priority=2)
    kb3.add(P, priority=1)

    print(f"\nKB3: {kb3}")
    print(f"  KB3 |= R           : {entails(kb3, R)}")          # True
    print(f"  KB3 |= ¬R          : {entails(kb3, Not(R))}")     # False

    # --- Empty KB entails nothing specific ---
    kb4 = BeliefBase()
    print(f"\nKB4 (empty): {kb4}")
    print(f"  KB4 |= P           : {entails(kb4, P)}")          # False
    print(f"  KB4 consistent    : {is_consistent(kb4)}")        # True
