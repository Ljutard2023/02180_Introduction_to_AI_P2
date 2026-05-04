import itertools
import random

def evaluate_feedback(secret_code: tuple, guess: tuple) -> tuple:
    """
    Compares guess to secret_code. 
    Returns (black_pegs, white_pegs).
    """
    # Black pegs: correct color and position
    blacks = sum(1 for s, g in zip(secret_code, guess) if s == g)
    
    # Total color matches (ignoring position)
    secret_counts = {c: secret_code.count(c) for c in set(secret_code)}
    guess_counts = {c: guess.count(c) for c in set(guess)}
    total_color_matches = sum(min(secret_counts.get(c, 0), guess_counts.get(c, 0)) for c in set(guess))
    
    # White pegs: total color matches minus black pegs
    whites = total_color_matches - blacks
    
    return (blacks, whites)

class PlausibilityOrder:
    def __init__(self, colors: list, positions: int):
        """
        Initializes the universe W of all possible worlds.
        Default plausibility rank is 0 (equal plausibility).
        """
        # Generate cartesian product (e.g., 6 colors ^ 4 positions = 1296 worlds)
        all_possible_worlds = list(itertools.product(colors, repeat=positions))
        
        # Map each world to its plausibility rank
        self.order = {world: 0 for world in all_possible_worlds}
        
    def get_most_plausible_worlds(self) -> list:
        """
        Returns a list of worlds with the lowest (best) rank.
        """
        best_rank = min(self.order.values())
        return [w for w, rank in self.order.items() if rank == best_rank]

    def revise(self, guess: tuple, actual_feedback: tuple):
        """
        Lexicographic revision. 
        Demotes worlds that contradict the actual feedback.
        """
        for world in self.order:
            if evaluate_feedback(world, guess) == actual_feedback:
                # World is consistent with feedback, keep current rank
                pass
            else:
                # World contradicts feedback; massive penalty applied
                self.order[world] += 1000

def minimax_guess(all_possible_worlds: list, plausible_worlds: list) -> tuple:
    """
    Selects the next guess by minimizing the worst-case scenario.
    """
    # Hardcode first guess to save computation time
    if len(plausible_worlds) == len(all_possible_worlds):
        return all_possible_worlds[0] 

    if len(plausible_worlds) == 1:
        return plausible_worlds[0]

    best_guess = None
    min_worst_case = float('inf')

    # Evaluate all possible guesses
    for guess in all_possible_worlds:
        feedback_counts = {}
        
        # Simulate guess against all currently plausible worlds
        for possible_secret in plausible_worlds:
            fb = evaluate_feedback(possible_secret, guess)
            feedback_counts[fb] = feedback_counts.get(fb, 0) + 1
            
        # The worst-case for this guess is the maximum number of survivors
        worst_case_for_this_guess = max(feedback_counts.values())

        # Minimize this worst-case
        if worst_case_for_this_guess < min_worst_case:
            min_worst_case = worst_case_for_this_guess
            best_guess = guess
            
            # Optimization: break if a perfect division is found
            if min_worst_case == 1:
                break 

    return best_guess

#  Autonomous controller (AI vs game)
if __name__ == "__main__":
    # Traditional Mastermind: 6 colors, 4 positions -> 1296 worlds
    COLORS = ['Red', 'Blue', 'Green', 'Yellow', 'Orange', 'Purple']
    POSITIONS = 4
    
    print("Initializing agent (Creating universe W)...")
    agent_beliefs = PlausibilityOrder(COLORS, POSITIONS)
    all_worlds = list(agent_beliefs.order.keys())
    
    # Game randomly selects secret code
    secret_code = random.choice(all_worlds)
    print("\n" + "="*50)
    print(" GAME START")
    print(f" (Secret code is: {secret_code})")
    print("="*50 + "\n")
    
    attempt = 1
    max_attempts = 10
    game_won = False
    
    while attempt <= max_attempts:
        plausible_worlds = agent_beliefs.get_most_plausible_worlds()
        print(f"--- Turn {attempt} ---")
        print(f"Plausible worlds remaining: {len(plausible_worlds)}")
        
        # 1. Agent computes next guess (Minimax)
        print("Agent is thinking (Minimax algorithm running)...")
        current_guess = minimax_guess(all_worlds, plausible_worlds)
        print(f" -> Agent proposes: {current_guess}")
        
        # Game evaluates and returns feedback
        feedback = evaluate_feedback(secret_code, current_guess)
        print(f" -> Game feedback: {feedback[0]} Black, {feedback[1]} White")
        
        # Win condition
        if feedback[0] == POSITIONS:
            print(f"\nSUCCESS! Agent cracked the code in {attempt} attempts.")
            game_won = True
            break
            
        # Agent revises its belief base
        print(" -> Agent revising plausibility order...\n")
        agent_beliefs.revise(current_guess, feedback)
        
        attempt += 1
        
    if not game_won:
        print("\nFAILURE. Agent could not find the code within the limit.")