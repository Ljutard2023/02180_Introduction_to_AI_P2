# ============================================================
#  STEP B - Conjunctive Normal Form (CNF) Conversion
# ============================================================

from formulas import Atom, Not, And, Or, Implies, Formula

def eliminate_implications(formula: Formula) -> Formula:
    """Replaces A → B with ¬A ∨ B."""
    if isinstance(formula, Atom):
        return formula
    elif isinstance(formula, Not):
        return Not(eliminate_implications(formula.formula))
    elif isinstance(formula, And):
        return And(eliminate_implications(formula.left), eliminate_implications(formula.right))
    elif isinstance(formula, Or):
        return Or(eliminate_implications(formula.left), eliminate_implications(formula.right))
    elif isinstance(formula, Implies):
        left = eliminate_implications(formula.left)
        right = eliminate_implications(formula.right)
        return Or(Not(left), right)

def push_negations(formula: Formula) -> Formula:
    """Applies De Morgan's laws to push negations to atoms."""
    if isinstance(formula, Atom):
        return formula
    elif isinstance(formula, Not):
        inner = formula.formula
        if isinstance(inner, Atom):
            return formula
        elif isinstance(inner, Not):
            return push_negations(inner.formula)
        elif isinstance(inner, And):
            return Or(push_negations(Not(inner.left)), push_negations(Not(inner.right)))
        elif isinstance(inner, Or):
            return And(push_negations(Not(inner.left)), push_negations(Not(inner.right)))
    elif isinstance(formula, And):
        return And(push_negations(formula.left), push_negations(formula.right))
    elif isinstance(formula, Or):
        return Or(push_negations(formula.left), push_negations(formula.right))

def distribute_or(formula: Formula) -> Formula:
    """Distributes ∨ over ∧."""
    if isinstance(formula, Atom):
        return formula
    elif isinstance(formula, Not):
        return formula
    elif isinstance(formula, And):
        return And(distribute_or(formula.left), distribute_or(formula.right))
    elif isinstance(formula, Or):
        left = distribute_or(formula.left)
        right = distribute_or(formula.right)

        if isinstance(right, And):
            return And(distribute_or(Or(left, right.left)), distribute_or(Or(left, right.right)))
        elif isinstance(left, And):
            return And(distribute_or(Or(left.left, right)), distribute_or(Or(left.right, right)))
        else:
            return Or(left, right)

def extract_clauses(formula: Formula) -> set:
    """Converts a CNF tree into a set of frozensets (clauses)."""
    if isinstance(formula, And):
        return extract_clauses(formula.left) | extract_clauses(formula.right)
    else:
        return {frozenset(extract_literals(formula))}

def extract_literals(formula: Formula) -> list:
    """Extracts literals from a single clause."""
    if isinstance(formula, Atom):
        return [formula]
    elif isinstance(formula, Not):
        return [formula]
    elif isinstance(formula, Or):
        return extract_literals(formula.left) + extract_literals(formula.right)

def to_cnf(formula: Formula) -> set:
    """Converts any formula to CNF clauses."""
    step1 = eliminate_implications(formula)
    step2 = push_negations(step1)
    step3 = distribute_or(step2)
    step4 = extract_clauses(step3)
    return step4

def clause_to_str(clause: frozenset) -> str:
    """Formats a clause as a readable string."""
    literals = sorted([str(lit) for lit in clause])
    return "(" + " ∨ ".join(literals) + ")"

def cnf_to_str(clauses: set) -> str:
    """Formats a CNF clause set as a readable string."""
    if not clauses:
        return "⊤ (Always true - empty base)"
    clause_strs = sorted([clause_to_str(c) for c in clauses])
    return " ∧\n".join(clause_strs)

# ============================================================
# DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print(" STEP B - CNF Conversion Demonstration")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    examples = [
        ("P → Q",          P >> Q),
        ("P → Q → R",      P >> (Q >> R)),
        ("¬(P ∧ Q)",       ~(P & Q)),
        ("¬(P ∨ Q)",       ~(P | Q)),
        ("(P → Q) → R",    (P >> Q) >> R),
        ("¬(P → Q)",       ~(P >> Q)),
    ]

    for name, formula in examples:
        print(f"\n{'─'*50}")
        print(f"  Formula: {name}")

        s1 = eliminate_implications(formula)
        print(f"  Step 1 (Eliminate →): {s1}")

        s2 = push_negations(s1)
        print(f"  Step 2 (Push ¬): {s2}")

        s3 = distribute_or(s2)
        print(f"  Step 3 (Distribute): {s3}")

        clauses = extract_clauses(s3)
        print(f"  Step 4 (Clauses):\n    {cnf_to_str(clauses)}")