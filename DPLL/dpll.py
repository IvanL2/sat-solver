from cnf_transformer import Transformer
from parser import Parser
from tree import Tree
from semantics import *


def add_semantics(ast: Tree):
    #Tree.add_depth_information(ast)
    Semantics.polarise(ast)
    Semantics.literal_marker(ast)
    ast.semantics = True

def dpll(exp):
    parsed = Parser.parse(exp)
    Parser.print_exp(parsed)
    add_semantics(parsed)
    clauses = Transformer.transform(parsed)
    print(f"RESULT FOR {exp}")
    for x in clauses:
        Parser.print_exp(x)

example_bad = "(a <-> b) -> c"
example = "((p <-> ~q) -> r) -> r /\~p"
example2 = "((a/\\b)\\/c)"
example3 ="((a -> b) & (c <-> d)) \\/ p & T"
example4 = "a /\ ¬a"
sat = dpll(example4)
dpll(example)
dpll(example2)
dpll(example3)