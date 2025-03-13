# SAT Solver

(Upcoming) Implementations of different SAT Solving algorithms; including the transform of arbitrary propositional formulas into CNF.

Current implementations: DPLL

### (Intended) Usage

#### DPLL (see dpll_example.py for example)
```python
from dpll import dpll, dpll_model, dpll_equiv, dpll_equiv_with_cex, dpll_valid, dpll_valid_with_cex
dpll("your prop. logic expr") -> bool #(True if satisfiable, False otherwise)
dpll_model("your prop. logic expr") -> List[Tuple[str, bool]] # The list of variables of the form (variable name, True/False)
dpll_equiv("prop_formula_1","prop_formula_2") -> bool
dpll_equiv_with_cex("prop_formula_1","prop_formula_2") -> List[Tuple[str, bool]]
dpll_valid("your prop. logic expr") -> bool
dpll_valid_with_cex("your prop. logic expr") -> List[Tuple[str, bool]]
```


The model returned by `dpll_model` is non-deterministic due to sets' unordered nature; the implementation of the DPLL algorithm simply picks the first value of list(set of clauses). The model may also be partial, however it will always return a correct result for any satisfiable expression, and None otherwise.
# License

This project is licensed under the terms of the [MIT License](LICENSE.md)


