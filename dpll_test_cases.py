from DPLL.dpll import dpll, dpll_model

example4 = "(a <-> b) -> c"
example = "((p <-> ~q) -> r) -> r /\~p"
example2 = "((a/\\b)\\/c)"
example3 ="((a -> b) & (c <-> d)) \\/ p & T"
example_unsat1 = "a /\ ¬a"
example_unsat2 = "(x \/ x \/ x) /\ (¬x \/ ¬x \/ ¬x)"
example_unsat3 = "(x | y | z) & (x | y | ¬z) & (x | ¬y | z) & (x | ¬y | ¬z) & (¬x | y | z) & (¬x | y | ¬x) & (¬x | ¬y | z) & (¬x | ¬y | ¬z)"
example_unsat4 = "b /\ c /\ c /\ c /\ ¬b /\ c"
example_unsat5 = "¬((p → q) ∧ (p ∧ q → r ) → (p → r ))"
example_f = "F"
example_t = "T"
example_t2 = "T /\ a"
example_f2 = "F /\ a"
example_f3 = "F \/ a"
example_tf = "T /\ F"
example_tf2 = "T \/ F"
example_empty = ""
example_long_nots = "¬¬a"
example_bad = ")a -> b("
example_bad2 = "()"
example_bad3 = "a(b \/ c)"
example_real = "!((a = b) = (a -> b))"
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

try:
    print(f"EXPRESSION: {example_bad}, RESULT: {'SAT' if dpll(example_bad) else 'UNSAT'}, EXPECTED: ERROR")
except SyntaxError:
    print(f"Successfully detected syntax error in {example_bad}.")

try:
    print(f"EXPRESSION: {example_bad2}, RESULT: {'SAT' if dpll(example_bad2) else 'UNSAT'}, EXPECTED: ERROR")
except SyntaxError:
    print(f"Successfully detected syntax error in {example_bad2}.")

try:
    print(f"EXPRESSION: {example_bad3}, RESULT: {'SAT' if dpll(example_bad3) else 'UNSAT'}, EXPECTED: ERROR")
except SyntaxError:
    print(f"Successfully detected syntax error in {example_bad3}.")

print(f"EXPRESSION: {example_real}, RESULT: {'SAT' if dpll(example_real) else 'UNSAT'}, EXPECTED: SAT")
