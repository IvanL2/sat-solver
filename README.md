# SAT Solver

Implementations of different SAT Solving algorithms learned from my course at the University of Manchester.


### (Intended) Usage

#### DPLL (see dpll.py for example)
Parser.parse("your expression") to produce an AST; structure defined in tree.py
Semantics.polarise(AST) to add polarity information to each node
Transformer(polarised AST) to produce a set of clauses (in CNF-SAT)
[TODO: Add actual solver]

### TODO:
- Fix DNF -> CNF implementation
- Fix solver
- Create pipeline wrapper for everything
- Add syntax check

# License

This project is licensed under the terms of the [MIT License](LICENSE.md)
