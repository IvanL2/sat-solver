from dpll import dpll

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
example_empty = ""
example_long_nots = "¬¬a"
print(f"EXPRESSION: {example}, RESULT: {'SAT' if dpll(example) else 'UNSAT'}, EXPECTED: SAT")
print(f"EXPRESSION: {example2}, RESULT: {'SAT' if dpll(example2) else 'UNSAT'}, EXPECTED: SAT")
print(f"EXPRESSION: {example3}, RESULT: {'SAT' if dpll(example3) else 'UNSAT'}, EXPECTED: SAT")
print(f"EXPRESSION: {example4}, RESULT: {'SAT' if dpll(example4) else 'UNSAT'}, EXPECTED: SAT")
print(f"EXPRESSION: {example_unsat1}, RESULT: {'SAT' if dpll(example_unsat1) else 'UNSAT'}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_unsat2}, RESULT: {'SAT' if dpll(example_unsat2) else 'UNSAT'}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_unsat3}, RESULT: {'SAT' if dpll(example_unsat3) else 'UNSAT'}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_unsat4}, RESULT: {'SAT' if dpll(example_unsat4) else 'UNSAT'}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_f}, RESULT: {'SAT' if dpll(example_f) else 'UNSAT'}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_t}, RESULT: {'SAT' if dpll(example_t) else 'UNSAT'}, EXPECTED: SAT")
print(f"EXPRESSION: {example_t2}, RESULT: {'SAT' if dpll(example_t2) else 'UNSAT'}, EXPECTED: SAT")
print(f"EXPRESSION: {example_f2}, RESULT: {'SAT' if dpll(example_f2) else 'UNSAT'}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_f3}, RESULT: {'SAT' if dpll(example_f3) else 'UNSAT'}, EXPECTED: SAT")
print(f"EXPRESSION: {example_tf}, RESULT: {'SAT' if dpll(example_tf) else 'UNSAT'}, EXPECTED: UNSAT")
print(f"EXPRESSION: {example_tf2}, RESULT: {'SAT' if dpll(example_tf2) else 'UNSAT'}, EXPECTED: SAT")
try:
    print(f"EXPRESSION: {example_empty}, RESULT: {'SAT' if dpll(example_empty) else 'UNSAT'}, EXPECTED: crash gracefully")
except:
    print(f"EXPRESSION: {example_empty} gracefully crashed!")
    pass
print(f"EXPRESSION: {example_long_nots}, RESULT: {'SAT' if dpll(example_long_nots) else 'UNSAT'}, EXPECTED: SAT")