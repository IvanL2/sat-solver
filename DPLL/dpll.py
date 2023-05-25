from cnf_transformer import Transformer
from parser import Parser
from solver import Solver
from tree import Tree
from semantics import *

def dpll(exp: str) -> str:
    parsed = Parser.parse(exp)
    clauses = Transformer.transform(parsed)
    return Solver.solve(clauses)
