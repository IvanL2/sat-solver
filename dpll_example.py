from DPLL.dpll import dpll, dpll_model


example = "((p <-> ~q) -> r) -> r /\~p"
example2 = "((a/\\b)\\/c)"
example3 ="((a -> b) & (c <-> d)) | p & T"
example4 = "(a <-> b) -> c"

print(f"EXPRESSION: {example3}, RESULT: {'SAT' if dpll(example3) else 'UNSAT'}, EXPECTED: SAT")
print(f"MODEL: {dpll_model(example3)}")

print(dpll_model("a \/ ¬a", verbose=True))

# If interested in submodules

from DPLL.pl_parser import Parser

ast = Parser.parse(example) # ast short for abstract syntax tree
Parser.print_exp(ast)       # Takes a tree and prints a reconstructed expression
# Parser.print_exp(ast)     # The output of this is quite ugly; the nodes of the tree are printed in depth-first fashion

from DPLL.cnf_transformer import Transformer
clauses = Transformer.transform(ast) # Transforms into a set of trees that represent the clauses of the CNF-SAT problem
#print(clauses)

from DPLL.solver import Solver
answer = Solver.solve(clauses) # Runs the DPLL algorithm, and returns True for satisfiable and False for unsat.
print(answer)

# Internally, converts tree clauses into sets of tuples of the form {(var_name, True if positive, False if negative), (var_name2, True/False)}
new_variables = [Solver.transform_to_variables(c) for c in clauses]
#print(new_variables)