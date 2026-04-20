# 02180_Introduction_to_AI_P2

# Belief Revision Agent - 02180 Intro to AI (DTU SP25)

## Overview
This repository contains the implementation of a Propositional Logic Belief Revision Engine, developed for the 02180 Introduction to AI course. The engine implements the AGM postulates for belief revision using a syntax-based approach with Epistemic Entrenchment (priority-ordered belief bases).

## Architecture & Project Status

The project is divided into modular components following the assignment's sequence of stages.

### 1. Foundational Logic (Completed)
* `formulas.py`: Abstract Syntax Tree (AST) representation of propositional logic formulas (Atoms, And, Or, Not, Implies), including basic evaluation and tautology checking.
* `cnf.py`: Conversion pipeline to translate any arbitrary propositional formula into Conjunctive Normal Form (CNF) using De Morgan's laws and distributivity.

### 2. Logical Entailment (To Do)
* `resolution.py`: Requires the implementation of a resolution-based refutation algorithm to check `KB ⊨ α`. 
* *Note to team: We should implement Set of Support (SoS) and subsumption to avoid combinatorial explosion.*

### 3. Belief Revision Core (To Do)
* `contraction.py`: Requires the implementation of partial meet contraction (or a greedy equivalent) to gracefully remove beliefs while respecting their priority order.
* `expansion.py`: Requires the implementation of blind expansion (`KB + α`) and Levi Identity revision (`KB * α`).

### 4. AGM Postulates Validation (Completed)
* `test_agm.py`: Automated test suite verifying our engine against the AGM postulates (Success, Inclusion, Vacuity, Consistency, Extensionality). 
* **Usage:** Run `python test_agm.py` to validate the implementation of the core engine. All tests must pass before we start the report.

### 5. Mastermind Extension (Pending)
* Implementation of the code-breaker AI using a plausibility order over possible worlds (semantic approach), as suggested by the assignment's alternative track.
