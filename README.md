# Belief Revision Agent & Mastermind AI
**02180 Introduction to AI**

## Project Overview
This repository implements a dual-architecture Belief Revision Engine, satisfying all requirements of the assignment. 
1. **Sections 1-3:** A syntactic engine handling propositional logic inference, greedy contraction based on epistemic entrenchment, and Levi Identity revision, strictly validated against the AGM postulates.
2. **Section 4 (Extension):** A semantic engine implementing belief revision over plausibility orders to solve the Mastermind game, bypassing the combinatorial explosion of CNF conversions.

## How to Run

```bash
python main.py      # Full scripted demo: syntactic pipeline, AGM validation, Mastermind
python agent.py     # Interactive terminal: build and query a belief base manually
python test_agm.py  # AGM postulate verification only
python mastermind.py  # Standalone Mastermind game (6 colours, 4 positions)
```

## Interactive Terminal (agent.py)

`agent.py` provides a menu-driven interface for interacting with the belief revision engine at runtime. This is the recommended entry point for testing with a custom knowledge base.

```
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
╚══════════════════════════════════════════════════╝
```

**Formula syntax:**
```
P                  atom
not P  or  ~P      negation
P and Q            conjunction
P or Q             disjunction
P -> Q             implication
(P -> Q) -> R      grouping with parentheses
```

Atom names can be any word.

## Mathematical Justification

The resolution algorithm by refutation seeks to prove $KB \models \alpha$ by demonstrating that the set $S = KB \cup \{\neg \alpha\}$ is unsatisfiable.

Let $\Delta$ be the set of clauses derived from the belief base $KB$, and $\Gamma$ be the set of clauses derived from $\neg \alpha$. The initial set is therefore $S_0 = \Delta \cup \Gamma$.

### Naive Approach

In the brute-force implementation, the algorithm generates the deductive closure of $S_0$ by exhaustively evaluating all possible pairs $(C_i, C_j) \in S_0 \times S_0$.
* If the knowledge base $\Delta$ contains $n$ clauses, the very first pass of the loop performs $\frac{n(n-1)}{2}$ comparisons purely within $\Delta$.
* With each iteration, the set grows quadratically, generating redundant clauses or tautologies that have absolutely no relevance to refuting $\alpha$. This results in an undirected combinatorial explosion.

### Optimization via the Set of Support (SoS) Restriction
The *Set of Support* (SoS) strategy imposes a fundamental restriction on the search tree based on a core theorem of resolution: **If a subset $\Delta$ is satisfiable, then any refutation of $\Delta \cup \Gamma$ must necessarily involve at least one clause from $\Gamma$ or one of its descendants.**

Since we establish as a premise that the belief base $KB$ (thus $\Delta$) is logically consistent, the contradiction $\square$ cannot possibly originate from $\Delta \times \Delta$. The optimized algorithm therefore partitions the search space and strictly forbids resolving two clauses from $\Delta$ together.

Formally, at iteration $k$, a resolvent $R$ is generated from $(C_i, C_j)$ if and only if:
$$C_i \in SoS_k \quad \text{and} \quad C_j \in (\Delta \cup SoS_k)$$
where $SoS_0 = \Gamma$, and $SoS_{k+1}$ contains the newly generated, non-subsumed resolvents.

### Complexity Impact
This restriction transforms an exhaustive, bottom-up search (blind *forward-chaining*) into a goal-directed search (*backward-chaining* anchored in $\neg \alpha$).
* By completely pruning the $\Delta \times \Delta$ search space, the branching factor of the resolution algorithm is severely restricted.
* By applying forward subsumption (rejecting any clause $C$ such that there exists $C' \in S$ where $C' \subseteq C$), we prevent memory saturation by destroying useless clauses on the fly.
* This makes the computation of the Levi Identity computationally viable in finite time, whereas the naive approach fundamentally fails to scale.
