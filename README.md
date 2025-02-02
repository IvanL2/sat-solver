# SAT Solver

Implementations of different SAT Solving algorithms learned from my course at the University of Manchester.


### (Intended) Usage

#### DPLL (see dpll_example.py for example)
```python
from dpll import dpll, dpll_model
dpll("your prop. logic expr") -> bool #(True if satisfiable, False otherwise)
dpll_model("your prop. logic expr") -> List[Tuple[str, bool]] # The list of variables of the form (variable name, True/False)
```

The model returned by `dpll_model` is non-deterministic due to sets' unordered nature; the implementation of the DPLL algorithm simply picks the first value of list(set of clauses). The model may also be partial, however it will always return a correct result for any satisfiable expression, and None otherwise.
# License

This project is licensed under the terms of the [MIT License](LICENSE.md)


#### Quick reference of equivalent problems
Formula A is **valid** if and only if ¬A is **unsatisfiable**; if a solution exists then **not valid** \
Formula A is **equivalent** to Formula B if and only iff ¬(A ↔ B) is **unsatisfiable**; if a solution exists then **not valid**
