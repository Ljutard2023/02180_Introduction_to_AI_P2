
from formulas import Atom, Not, And, Or, Implies, BeliefBase, Formula
from resolution import entails, is_consistent
from contraction import contract
from expansion import expand, revise


#  FORMULA PARSER
#
#  Accepts plain English syntax:
#    Atoms   : any uppercase or lowercase word, e.g. P, Q, Rain
#    Not     : "not X"  or  "~X"
#    And     : "X and Y"
#    Or      : "X or Y"
#    Implies : "X -> Y"
#    Grouping: parentheses, e.g. "(P -> Q) -> R"

class ParseError(Exception):
    pass

class _Tokenizer:
    """Breaks an input string into a flat list."""

    def __init__(self, text: str):
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _tokenize(self, text: str) -> list:
        tokens = []
        i = 0
        text = text.strip()
        while i < len(text):
            if text[i].isspace():
                i += 1
            elif text[i] == '(':
                tokens.append('('); i += 1
            elif text[i] == ')':
                tokens.append(')'); i += 1
            elif text[i:i+2] == '->':
                tokens.append('->'); i += 2
            elif text[i] == '~':
                tokens.append('not'); i += 1
            else:
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                if j == i:
                    raise ParseError(f"Unexpected character: '{text[i]}'")
                tokens.append(text[i:j])
                i = j
        return tokens

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        tok = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        if expected and tok != expected:
            raise ParseError(f"Expected '{expected}', got '{tok}'")
        self.pos += 1
        return tok

    def end(self):
        return self.pos >= len(self.tokens)


def _parse_implies(t: _Tokenizer) -> Formula:
    """Parses implication (lowest precedence, right-associative)."""
    left = _parse_or(t)
    if t.peek() == '->':
        t.consume('->')
        right = _parse_implies(t)
        return Implies(left, right)
    return left

def _parse_or(t: _Tokenizer) -> Formula:
    left = _parse_and(t)
    while t.peek() == 'or':
        t.consume('or')
        right = _parse_and(t)
        left = Or(left, right)
    return left

def _parse_and(t: _Tokenizer) -> Formula:
    left = _parse_not(t)
    while t.peek() == 'and':
        t.consume('and')
        right = _parse_not(t)
        left = And(left, right)
    return left

def _parse_not(t: _Tokenizer) -> Formula:
    if t.peek() == 'not':
        t.consume('not')
        operand = _parse_not(t)   # allows chaining: not not P
        return Not(operand)
    return _parse_atom(t)

def _parse_atom(t: _Tokenizer) -> Formula:
    tok = t.peek()
    if tok == '(':
        t.consume('(')
        expr = _parse_implies(t)
        t.consume(')')
        return expr
    if tok is None:
        raise ParseError("Unexpected end of input.")
    if tok in ('and', 'or', 'not', '->', ')', None):
        raise ParseError(f"Expected atom or '(', got '{tok}'")
    t.consume()
    return Atom(tok)

def parse_formula(text: str) -> Formula:
    """Parses a formula string into a Formula object.

    Syntax:
        Atoms   : any word,  e.g.  P  Rain  alive
        Not     : not P   or  ~P
        And     : P and Q
        Or      : P or Q
        Implies : P -> Q
        Groups  : (P -> Q) -> R

    Raises ParseError on invalid input.
    """
    text = text.strip()
    if not text:
        raise ParseError("Empty input.")
    t = _Tokenizer(text)
    result = _parse_implies(t)
    if not t.end():
        raise ParseError(f"Unexpected token after formula: '{t.peek()}'")
    return result


#  Display

def _show_kb(kb: BeliefBase):
    if kb.is_empty():
        print("  Belief base is empty.")
    else:
        for p, f in kb.beliefs:
            print(f"  [{p:>3}]  {f}")

def _divider():
    print("  " + "-" * 48)


def run_cli():
    kb = BeliefBase()

    MENU = """
╔══════════════════════════════════════════════════╗
║       BELIEF REVISION — Interactive Terminal     ║
╠══════════════════════════════════════════════════╣
║  0. Load example belief base                     ║
║  1. Show belief base                             ║
║  2. Contract          (KB ÷ α)                   ║
║  3. Expand            (KB + α)                   ║
║  4. Revise            (KB * α)                   ║
║  5. Add belief                                   ║
║  6. Remove belief                                ║
║  7. Check entailment  (KB ⊨ α?)                  ║
║  8. Check consistency                            ║
║  9. Exit                                         ║
╚══════════════════════════════════════════════════╝"""

    SYNTAX = ("  Formula syntax:  P   not P   P and Q   "
              "P or Q   P -> Q   (P -> Q) -> R")

    print(MENU)
    print(SYNTAX)

    while True:
        print()
        try:
            choice = input("  > Enter option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            break

        # Exit
        if choice == '9':
            print("  Goodbye.")
            break
        # Load weather domain KB
        elif choice == '0':
            print("  Loading weather domain knowledge base...")
            kb = BeliefBase()
            kb.add(Implies(Atom("Rain"), Atom("Wet")),                          priority=5)
            kb.add(Implies(And(Atom("Rain"), Atom("Umbrella")), Atom("Safe")), priority=4)
            kb.add(Atom("Rain"),                                                   priority=3)
            kb.add(Atom("Umbrella"),                                               priority=2)
            print("  Loaded: Rain->Wet, Rain and Umbrella->Safe, Rain, Umbrella")
            print("  Suggested tests:")
            print("    7 -> Wet        (should be True)")
            print("    7 -> Safe       (should be True)")
            print("    2 -> Rain       (contract: remove Rain belief)")
            print("    4 -> not Rain   (revise: it stopped raining)")
            _show_kb(kb)

        # Show KB
        elif choice == '1':
            print()
            _show_kb(kb)

        # Contract
        elif choice == '2':
            try:
                raw = input("  > Formula to contract by (KB ÷ α): ").strip()
                formula = parse_formula(raw)
                kb = contract(kb, formula, verbose=False)
                print(f"  Contracted by {formula}. New belief base:")
                _show_kb(kb)
            except ParseError as e:
                print(f"  [Parse error] {e}")

        # Expand
        elif choice == '3':
            try:
                raw = input("  > Formula to expand with (KB + α): ").strip()
                formula = parse_formula(raw)
                raw_p = input("  > Priority (integer, default auto): ").strip()
                priority = int(raw_p) if raw_p else None
                kb = expand(kb, formula, priority=priority, verbose=False)
                print(f"  Expanded with {formula}. New belief base:")
                _show_kb(kb)
            except ParseError as e:
                print(f"  [Parse error] {e}")
            except ValueError:
                print("  [Error] Priority must be an integer.")

        # Revise
        elif choice == '4':
            try:
                raw = input("  > Formula to revise with (KB * α): ").strip()
                formula = parse_formula(raw)
                raw_p = input("  > Priority (integer, default auto): ").strip()
                priority = int(raw_p) if raw_p else None
                kb = revise(kb, formula, priority=priority, verbose=False)
                print(f"  Revised with {formula}. New belief base:")
                _show_kb(kb)
            except ParseError as e:
                print(f"  [Parse error] {e}")
            except ValueError:
                print("  [Error] Priority must be an integer.")

        # Add belief
        elif choice == '5':
            try:
                raw = input("  > Formula to add: ").strip()
                formula = parse_formula(raw)
                raw_p = input("  > Priority (integer, default 1): ").strip()
                priority = int(raw_p) if raw_p else 1
                kb.add(formula, priority=priority)
                print(f"  Added: {formula}  (priority {priority})")
            except ParseError as e:
                print(f"  [Parse error] {e}")
            except ValueError:
                print("  [Error] Priority must be an integer.")

        # Remove belief
        elif choice == '6':
            try:
                raw = input("  > Formula to remove: ").strip()
                formula = parse_formula(raw)
                before = len(kb.beliefs)
                kb.remove(formula)
                if len(kb.beliefs) < before:
                    print(f"  Removed: {formula}")
                else:
                    print(f"  Not found in belief base: {formula}")
            except ParseError as e:
                print(f"  [Parse error] {e}")

        # Entailment
        elif choice == '7':
            try:
                raw = input("  > Formula to check (KB ⊨ α?): ").strip()
                formula = parse_formula(raw)
                result = entails(kb, formula)
                print(f"  KB ⊨ {formula}:  {result}")
            except ParseError as e:
                print(f"  [Parse error] {e}")

        # Consistency
        elif choice == '8':
            result = is_consistent(kb)
            print(f"  KB is consistent: {result}")

        # Unknown
        else:
            print("  Unknown option. Enter a number from 1 to 9.")


if __name__ == "__main__":
    run_cli()
