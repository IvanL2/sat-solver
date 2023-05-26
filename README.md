# SAT Solver

Implementations of different SAT Solving algorithms learned from my course at the University of Manchester.


### (Intended) Usage

#### DPLL (see example.py for example)
```python
from dpll import dpll
dpll("your prop. logic expr") -> bool #(True if satisfiable, False otherwise)
dpll_model("your prop. logic expr") -> List[Tuple[str, bool]] # The list of variables of the form (variable name, True/False)
```

The model returned by `dpll_model` is non-deterministic due to sets' unordered nature; the implementation of the DPLL algorithm simply picks the first value of list(set of clauses). The model may also be partial, however it will always return a correct result for any satisfiable expression, and None otherwise.
### TODO:
- Add syntax check

# License

This project is licensed under the terms of the [MIT License](LICENSE.md)
