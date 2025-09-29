from dpll.cnf_transformer import Transformer
from dpll.logic_tree import LogicTree
from dpll.parser import Parser
from dpll.solver import Solver, SolverVariable


def dpll(exp: str) -> bool:
    """Returns True if the given expression is satisfiable, False if unsatisfiable."""

    parsed = Parser.parse(exp)

    clauses = Transformer.transform(parsed)

    return (Solver.solve(clauses)).satisfiable


def dpll_model(exp: str) -> list[SolverVariable] | None:
    """Returns a (maybe partial) model if satisfiable, None if unsatisfiable.
    This means that it may return an empty list [], if the given expression is a tautology."""

    parsed = Parser.parse(exp)
    original_vars = LogicTree.get_var_names(parsed)

    clauses = Transformer.transform(parsed)

    solution = Solver.solve(clauses)
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
    return not dpll(formula)


def dpll_valid_with_cex(expr: str, verbose: bool = False) -> list[SolverVariable] | None:
    formula = f"¬({expr})"
    if verbose:
        print(f"Check if {formula} is UNSAT")
    return dpll_model(formula)


def dpll_equiv(expr1: str, expr2: str, verbose: bool = False) -> bool:
    formula = f"¬(({expr1}) = ({expr2}))"
    if verbose:
        print(f"Check if {formula} is UNSAT")
    return not dpll(formula)


def dpll_equiv_with_cex(expr1: str, expr2: str) -> list[SolverVariable] | None:
    formula = f"¬(({expr1}) = ({expr2}))"
    return dpll_model(formula)
