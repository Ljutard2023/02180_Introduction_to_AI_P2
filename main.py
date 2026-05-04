import sys
from formulas import Atom, BeliefBase, Not, And
from resolution import entails, is_consistent
from contraction import contract
from expansion import revise
import test_agm
import mastermind
import random

def run_syntactic_pipeline():
    print("=" * 60)
    print(" PART 1: SYNTACTIC BELIEF REVISION (SECTIONS 1-3)")
    print("=" * 60)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    print("\n[1.1] Initializing Belief Base with priorities...")
    kb = BeliefBase()
    kb.add(P >> Q, priority=10)
    kb.add(Q >> R, priority=5)
    kb.add(P, priority=1)
    
    print(f"Current Base: {[str(f) for f in kb.get_formulas()]}")
    print(f"KB entails R? {entails(kb, R)}")

    print("\n[1.2] Belief Contraction (Greedy Approach)...")
    target = R
    print(f"Contracting KB by {target}...")
    kb_contracted = contract(kb, target)
    print(f"KB after contraction entails R? {entails(kb_contracted, target)}")

    print("\n[1.3] Belief Revision (Levi Identity)...")
    new_belief = Not(Q)
    print(f"Revising KB by {new_belief}...")
    kb_revised = revise(kb, new_belief, priority=8)
    print(f"Revised Base: {[str(f) for f in kb_revised.get_formulas()]}")
    print(f"Is revised base consistent? {is_consistent(kb_revised)}")

def run_agm_validation():
    print("\n" + "=" * 60)
    print(" PART 2: AGM POSTULATES VALIDATION")
    print("=" * 60)

    P = Atom("P")
    Q = Atom("Q")
    R = Atom("R")

    # Revision postulates
    # Scenario 1: KB entails ¬α — exercises Success, Inclusion,
    # Consistency, Extensionality. Vacuity prints N/A (correct).
    print("\n[2.1] Revision postulates — KB={P→Q, P}, α=¬Q")
    kb1 = BeliefBase()
    kb1.add(P >> Q, priority=2, verbose=False)
    kb1.add(P, priority=1, verbose=False)
    alpha = Not(Q)

    test_agm.test_agm_success(kb1, alpha)
    test_agm.test_agm_inclusion(kb1, alpha)
    test_agm.test_agm_vacuity(kb1, alpha)
    test_agm.test_agm_consistency(kb1, alpha)

    alpha_ext = Not(And(P, Q))
    beta_ext  = Atom("P") >> Not(Q)
    test_agm.test_agm_extensionality(kb1, alpha_ext, beta_ext)

    # Scenario 2: KB does NOT entail ¬α — Vacuity fires.
    # KB={R} has no conflict with P, so K*P = K+P.
    print("\n[2.2] Revision postulates — KB={R}, α=P (Vacuity fires)")
    kb2 = BeliefBase()
    kb2.add(R, priority=1, verbose=False)
    test_agm.test_agm_vacuity(kb2, P)

    # Contraction postulates
    print("\n[2.3] Contraction postulates — KB={P→Q, P}, α=Q")
    kb3 = BeliefBase()
    kb3.add(P >> Q, priority=2, verbose=False)
    kb3.add(P, priority=1, verbose=False)

    test_agm.test_contraction_success(kb3, Q)
    test_agm.test_contraction_inclusion(kb3, Q) 
    test_agm.test_contraction_vacuity(kb3, R) 

def run_semantic_pipeline():
    print("\n" + "=" * 60)
    print(" PART 3: SEMANTIC BELIEF REVISION (MASTERMIND EXTENSION)")
    print("=" * 60)
    
    COLORS = ['Rouge', 'Bleu', 'Vert', 'Jaune']
    POSITIONS = 3
    print(f"Initializing Plausibility Order (Universe W = {len(COLORS)**POSITIONS} worlds)...")
    agent_beliefs = mastermind.PlausibilityOrder(COLORS, POSITIONS)
    all_worlds = list(agent_beliefs.order.keys())
    
    secret_code = random.choice(all_worlds)
    print(f"Target Secret Code (Hidden): {secret_code}")
    
    attempt = 1
    while attempt <= 5:
        plausible_worlds = agent_beliefs.get_most_plausible_worlds()
        print(f"\n--- Turn {attempt} ---")
        print(f"Plausible worlds remaining: {len(plausible_worlds)}")
        
        guess = mastermind.minimax_guess(all_worlds, plausible_worlds)
        feedback = mastermind.evaluate_feedback(secret_code, guess)
        
        print(f"Agent Guess: {guess} -> Feedback: {feedback[0]} Black, {feedback[1]} White")
        
        if feedback[0] == POSITIONS:
            print("Code cracked successfully.")
            break
            
        agent_beliefs.revise(guess, feedback)
        attempt += 1

if __name__ == "__main__":
    run_syntactic_pipeline()
    run_agm_validation()
    run_semantic_pipeline()