#  Step C - Resolution Algorithm

from formulas import Formula, BeliefBase, Not
from cnf import to_cnf

def get_opposite(literal: Formula) -> Formula:
    """Returns the logical opposite of a literal."""
    if isinstance(literal, Not):
        return literal.formula
    return Not(literal)

def resolve(clause1: frozenset, clause2: frozenset) -> list:
    """Generates resolvents from two clauses."""
    resolvents = []
    for literal in clause1:
        opposite = get_opposite(literal)
        if opposite in clause2:
            new_clause = (clause1 - {literal}) | (clause2 - {opposite})
            resolvents.append(frozenset(new_clause))
    return resolvents

def is_subsumed(clause: frozenset, clause_set: set) -> bool:
    """Checks if 'clause' is a superset of an existing clause (redundant)."""
    for existing_clause in clause_set:
        if existing_clause.issubset(clause):
            return True
    return False

def resolution_sos(background_clauses: set, target_clauses: set) -> bool:
    """Refutation resolution using Set of Support and forward subsumption."""
    processed = set(background_clauses)
    unprocessed = list(target_clauses)

    while unprocessed:
        # Unit preference heuristic
        unprocessed.sort(key=len)
        current = unprocessed.pop(0)

        if len(current) == 0:
            return True

        new_clauses = []
        
        for p in processed:
            resolvents = resolve(current, p)
            
            for r in resolvents:
                if len(r) == 0:
                    return True
                
                if not is_subsumed(r, processed) and not is_subsumed(r, set(unprocessed)):
                    new_clauses.append(r)

        processed.add(current)
        
        for nc in new_clauses:
            if nc not in unprocessed:
                unprocessed.append(nc)

    return False

def entails(kb: BeliefBase, alpha: Formula) -> bool:
    """Checks KB ⊨ α via SoS refutation."""
    background = set()
    for formula in kb.get_formulas():
        background |= to_cnf(formula)

    sos = to_cnf(Not(alpha))
    
    return resolution_sos(background, sos)

def is_consistent(kb: BeliefBase) -> bool:
    """Checks if KB is logically consistent internally."""
    all_clauses = set()
    for formula in kb.get_formulas():
        all_clauses |= to_cnf(formula)
        
    return not resolution_sos(set(), all_clauses)

# Demonstration

if __name__ == "__main__":
    from formulas import Atom
    
    print("=" * 55)
    print(" STEP C - Resolution (SoS) Demonstration")
    print("=" * 55)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    kb = BeliefBase()
    kb.add(P >> Q)
    kb.add(Q >> R)
    kb.add(P)

    print(f"Base: {[str(f) for f in kb.get_formulas()]}")
    print(f"KB ⊨ R ? -> {entails(kb, R)}")