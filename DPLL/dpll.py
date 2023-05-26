from cnf_transformer import Transformer
from parser import Parser
from solver import Solver
from tree import Tree
from semantics import *
from typing import Tuple, List

def dpll(exp: str) -> Tuple[bool, List[Tuple[str, bool]]]:
    parsed = Parser.parse(exp)
    clauses = Transformer.transform(parsed)
    return Solver.solve(clauses)[0]

def dpll_model(exp: str) -> Tuple[bool, List[Tuple[str, bool]]]:
    parsed = Parser.parse(exp)
    original_vars = Parser.get_variable_names(parsed)
    clauses = Transformer.transform(parsed)
    model_with_names = Solver.solve(clauses)[1]
    return list(filter(lambda x: (x[0] in original_vars) and (x[0] != "⊤") and (x[0] != "⊥"), model_with_names))