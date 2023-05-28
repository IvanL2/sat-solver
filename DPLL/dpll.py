from .cnf_transformer import Transformer
from .pl_parser import Parser
from .solver import Solver
from .tree import Tree
from .semantics import *
from typing import Tuple, List

def dpll(exp: str, verbose=False) -> bool:
    """Returns True if the given expression is satisfiable, False if unsatisfiable."""
    if verbose: print("========== PARSER START ==========")
    parsed = Parser.parse(exp, verbose)
    if verbose: print("========== TRANSFORM START ==========")
    clauses = Transformer.transform(parsed, verbose)
    if verbose: print("========== SOLVER START ==========")
    return Solver.solve(clauses, verbose)[0]

def dpll_model(exp: str, verbose=False) -> List[Tuple[str, bool]]:
    """Returns a (maybe partial) model if satisfiable, None if unsatisfiable.
    This means that it may return an empty list [], if the given expression is a tautology."""
    if verbose: print("========== PARSER START ==========")
    parsed = Parser.parse(exp, verbose)
    original_vars = Parser.get_variable_names(parsed)
    if verbose: print("========== TRANSFORM START ==========")
    clauses = Transformer.transform(parsed, verbose)
    if verbose: print("========== SOLVER START ==========")
    solution = Solver.solve(clauses, verbose)
    if solution[0]:
        model_with_names = solution[1]
        return list(filter(lambda x: (x[0] in original_vars) and (x[0] != "⊤") and (x[0] != "⊥"), model_with_names))
    else:
        return None