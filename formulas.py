# ============================================================
#  STEP A - Propositional Logic Formulas Representation
# ============================================================

class Formula:
    """Base class for all formulas."""
    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)

    def __rshift__(self, other):
        return Implies(self, other)

    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(str(self))

class Atom(Formula):
    """Atomic variable (e.g., P, Q)."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

class Not(Formula):
    """Negation: ¬φ"""
    def __init__(self, formula: Formula):
        self.formula = formula

    def __repr__(self):
        return f"¬{self.formula}"

class And(Formula):
    """Conjunction: φ ∧ ψ"""
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} ∧ {self.right})"

class Or(Formula):
    """Disjunction: φ ∨ ψ"""
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} ∨ {self.right})"

class Implies(Formula):
    """Implication: φ → ψ"""
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} → {self.right})"

class BeliefBase:
    """Set of prioritized formulas. Higher integer = higher priority."""
    def __init__(self):
        self.beliefs = []

    def add(self, formula: Formula, priority: int = 1):
        """Adds a prioritized formula."""
        for _, f in self.beliefs:
            if f == formula:
                print(f"  [Info] {formula} is already in the base.")
                return
        self.beliefs.append((priority, formula))
        self.beliefs.sort(key=lambda x: x[0], reverse=True)
        print(f"  [+] Added: {formula} (priority {priority})")

    def remove(self, formula: Formula):
        """Removes a formula."""
        before = len(self.beliefs)
        self.beliefs = [(p, f) for (p, f) in self.beliefs if f != formula]
        if len(self.beliefs) < before:
            print(f"  [-] Removed: {formula}")
        else:
            print(f"  [Info] {formula} not found in base.")

    def get_formulas(self):
        """Returns formulas without priorities."""
        return [f for (_, f) in self.beliefs]

    def is_empty(self):
        return len(self.beliefs) == 0

    def __repr__(self):
        if self.is_empty():
            return "BeliefBase { empty }"
        lines = ["BeliefBase {"]
        for priority, formula in self.beliefs:
            lines.append(f"  priority {priority} : {formula}")
        lines.append("}")
        return "\n".join(lines)

# ============================================================
# UTILITIES
# ============================================================

def get_atoms(formula: Formula) -> set:
    """Returns all unique atomic variables in a formula."""
    if isinstance(formula, Atom):
        return {formula.name}
    elif isinstance(formula, Not):
        return get_atoms(formula.formula)
    elif isinstance(formula, (And, Or, Implies)):
        return get_atoms(formula.left) | get_atoms(formula.right)
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")

def evaluate(formula: Formula, valuation: dict) -> bool:
    """Evaluates a formula given a dictionary of boolean valuations."""
    if isinstance(formula, Atom):
        if formula.name not in valuation:
            raise ValueError(f"Variable '{formula.name}' not defined in valuation.")
        return valuation[formula.name]
    elif isinstance(formula, Not):
        return not evaluate(formula.formula, valuation)
    elif isinstance(formula, And):
        return evaluate(formula.left, valuation) and evaluate(formula.right, valuation)
    elif isinstance(formula, Or):
        return evaluate(formula.left, valuation) or evaluate(formula.right, valuation)
    elif isinstance(formula, Implies):
        left_val = evaluate(formula.left, valuation)
        right_val = evaluate(formula.right, valuation)
        return (not left_val) or right_val
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")

def is_tautology(formula: Formula) -> bool:
    """Checks if a formula is true for all possible valuations."""
    atoms = list(get_atoms(formula))
    n = len(atoms)

    for i in range(2 ** n):
        valuation = {}
        for j, atom in enumerate(atoms):
            valuation[atom] = bool((i >> j) & 1)
        if not evaluate(formula, valuation):
            return False
    return True

def is_contradiction(formula: Formula) -> bool:
    """Checks if a formula is false for all possible valuations."""
    return is_tautology(Not(formula))

# ============================================================
# DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print(" STEP A - Demonstration")
    print("=" * 50)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    print("\n--- Constructed Formulas ---")
    f1 = P >> Q
    f2 = Q >> R
    f3 = P & Q
    f4 = P | ~Q
    f5 = ~(P & Q)
    f6 = (~P) | (~Q)

    print(f"f1 = {f1}")
    print(f"f2 = {f2}")
    print(f"f3 = {f3}")
    print(f"f4 = {f4}")
    print(f"f5 = {f5}")
    print(f"f6 = {f6}")

    print("\n--- Atoms in f1 ---")
    print(f"  Atoms of {f1}: {get_atoms(f1)}")

    print("\n--- Evaluation ---")
    valuation = {"P": True, "Q": False}
    print(f"  Valuation: {valuation}")
    print(f"  {f1} evaluates to: {evaluate(f1, valuation)}")
    print(f"  {f4} evaluates to: {evaluate(f4, valuation)}")

    print("\n--- Tautologies ---")
    taut = P | ~P
    cont = P & ~P
    print(f"  {taut} is a tautology: {is_tautology(taut)}")
    print(f"  {cont} is a contradiction: {is_contradiction(cont)}")
    print(f"  {f5} == {f6} : {is_tautology(f5 >> f6) and is_tautology(f6 >> f5)}")

    print("\n--- Belief Base ---")
    kb = BeliefBase()
    kb.add(f1, priority=3)
    kb.add(f2, priority=2)
    kb.add(P,  priority=1)
    print(kb)

    print("\n  Removing Q → R:")
    kb.remove(f2)
    print(kb)