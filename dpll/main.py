from typing import Tuple, List
from dpll.cnf_transformer import Transformer
from dpll.parser import Parser
from dpll.solver import Solver, SolverVariable


def dpll(exp: str, verbose: bool = False) -> bool:
    """Returns True if the given expression is satisfiable, False if unsatisfiable."""

    if verbose:
        print("=========== PARSER START ===========")
    parsed = Parser.parse(exp, verbose)

    if verbose:
        print("========== TRANSFORM START ==========")
    clauses = Transformer.transform(parsed, verbose)

    if verbose:
        print("========== SOLVER START ==========")
    return (Solver.solve(clauses, verbose)).satisfiable


def dpll_model(exp: str, verbose: bool = False) -> List[SolverVariable]:
    """Returns a (maybe partial) model if satisfiable, None if unsatisfiable.
    This means that it may return an empty list [], if the given expression is a tautology."""

    if verbose:
        print("========== PARSER START ==========")

    parsed = Parser.parse(exp, verbose)
    original_vars = Parser.get_variable_names(parsed)

    if verbose:
        print("========== TRANSFORM START ==========")

    clauses = Transformer.transform(parsed, verbose)

    if verbose:
        print("========== SOLVER START ==========")

    solution = Solver.solve(clauses, verbose)
    if solution.satisfiable:
        model_with_names = solution.model

        # Remove definitions introduced during tseytin transform; they do not affect satisfiability
        return list(filter(lambda x: (x[0] in original_vars) and (x[0] != "⊤") and (x[0] != "⊥"), model_with_names))
    else:
        return None

# Util methods


def dpll_valid(expr: str, verbose: bool = False) -> bool:
    formula = f"¬({expr})"
    if verbose:
        print(f"Check if {formula} is UNSAT")
    return not dpll(formula, verbose=verbose)


def dpll_valid_with_cex(expr: str, verbose: bool = False) -> List[Tuple[str, bool]]:
    formula = f"¬({expr})"
    if verbose:
        print(f"Check if {formula} is UNSAT")
    return dpll_model(formula, verbose=verbose)


def dpll_equiv(expr1: str, expr2: str, verbose: bool = False) -> bool:
    formula = f"¬(({expr1}) = ({expr2}))"
    if verbose:
        print(f"Check if {formula} is UNSAT")
    return not dpll(formula, verbose=verbose)


def dpll_equiv_with_cex(expr1: str, expr2: str, verbose: bool = False) -> List[Tuple[str, bool]]:
    formula = f"¬(({expr1}) = ({expr2}))"
    if verbose:
        print(f"Check if {formula} is UNSAT")
    return dpll_model(formula, verbose=verbose)
