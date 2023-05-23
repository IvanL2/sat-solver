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
    add_semantics(parsed)
    clauses = Transformer.transform(parsed)

example_bad = "(a <-> b) -> c"
example = "((p <-> ~q) -> r) -> r /\~p"
example2 = "((a/\\b)\\/c)"
example3 ="((a -> b) & (c <-> d)) \\/ p & T"

sat = dpll(example_bad)
