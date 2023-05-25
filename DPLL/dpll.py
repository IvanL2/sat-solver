from cnf_transformer import Transformer
from parser import Parser
from solver import Solver
from tree import Tree
from semantics import *

def dpll(exp: str) -> str:
    parsed = Parser.parse(exp)
    clauses = Transformer.transform(parsed)
    return "SAT" if Solver.solve(clauses) else "UNSAT"
    

example4 = "(a <-> b) -> c"
example = "((p <-> ~q) -> r) -> r /\~p"
example2 = "((a/\\b)\\/c)"
example3 ="((a -> b) & (c <-> d)) \\/ p & T"
example_unsat1 = "a /\ ¬a"
example_unsat2 = "(x \/ x \/ x) /\ (¬x \/ ¬x \/ ¬x)"
example_unsat3 = "(x v y v z) n (x v y v ¬z) n (x v ¬y v z) n (x v ¬y v ¬z) n (¬x v y v z) n (¬x v y v ¬x) n (¬x v ¬y v z) n (¬x v ¬y v ¬z)"
example_unsat4 = "b /\ c /\ c /\ c /\ ¬b /\ c"
example_f = "F"
example_t = "T"
example_t2 = "T /\ a"
example_f2 = "F /\ a"
example_f3 = "F \/ a"
example_tf = "T /\ F"
example_tf2 = "T \/ F"
print(f"EXPRESSION: {example}, RESULT: {dpll(example)}, EXPECTED: SAT")
print(f"EXPRESSION: {example2}, RESULT: {dpll(example2)}, EXPECTED: SAT")
print(f"EXPRESSION: {example3}, RESULT: {dpll(example3)}, EXPECTED: SAT")
print(f"EXPRESSION: {example4}, RESULT: {dpll(example4)}, EXPECTED: SAT")
print(f"EXPRESSION: {example_unsat1}, RESULT: {dpll(example_unsat1)}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_unsat2}, RESULT: {dpll(example_unsat2)}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_unsat3}, RESULT: {dpll(example_unsat3)}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_unsat4}, RESULT: {dpll(example_unsat4)}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_f}, RESULT: {dpll(example_f)}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_t}, RESULT: {dpll(example_t)}, EXPECTED: SAT")
print(f"EXPRESSION: {example_t2}, RESULT: {dpll(example_t2)}, EXPECTED: SAT")
print(f"EXPRESSION: {example_f2}, RESULT: {dpll(example_f2)}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_f3}, RESULT: {dpll(example_f3)}, EXPECTED: SAT")
print(f"EXPRESSION: {example_tf}, RESULT: {dpll(example_tf)}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_tf2}, RESULT: {dpll(example_tf2)}, EXPECTED: SAT")