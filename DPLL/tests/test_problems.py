# Check valid propositional expressions

import unittest
import pytest
from DPLL.dpll import dpll, dpll_model

class ProblemsTest(unittest.TestCase):
    example4 = "(a <-> b) -> c"
    example = "((p <-> ~q) -> r) -> r /\\ ~p"
    example2 = "((a/\\b)\\/c)"
    example3 ="((a -> b) && (c <-> d)) \\/ p && T"
    example_unsat1 = "a /\\ ¬a"
    example_unsat2 = "(x\\/ x\\/ x) /\\ (¬x\\/ ¬x\\/ ¬x)"
    example_unsat3 = "(x || y || z) && (x || y || ¬z) && (x || ¬y || z) && (x || ¬y || ¬z) && (¬x || y || z) && (¬x || y || ¬x) && (¬x || ¬y || z) && (¬x || ¬y || ¬z)"
    example_unsat4 = "b /\\ c /\\ c /\\ c /\\ ¬b /\\ c"
    example_unsat5 = "¬((p → q) ∧ (p ∧ q → r ) → (p → r ))"
    example_f = "F"
    example_t = "T"
    example_t2 = "T /\\ a"
    example_f2 = "F /\\ a"
    example_f3 = "F\\/ a"
    example_tf = "T /\\ F"
    example_tf2 = "T\\/ F"
    example_long_nots = "¬¬a"
    example_real = "!((a = b) = (a -> b))"
    example_sunny = "(sunny -> sunglasses) <-> (!sunny -> !sunglasses)"

    sat_cases = [
        example, example2, example3, example4, example_t, example_t2, example_f3, example_tf2,
        example_long_nots,
        example_real, example_sunny
    ]

    unsat_cases = [
        example_unsat1, example_unsat2, example_unsat3, example_unsat4, example_unsat5, example_f, example_f2, example_tf
    ]

    def test_sat(self):
        for case in self.sat_cases:
            self.assertTrue(dpll(case), f"Problem: {case}, expected SAT, returned UNSAT")
            self.assertIsNotNone(dpll_model(case), f"Problem: {case}, expected SAT, returned UNSAT")
    
    def test_unsat(self):
        for case in self.unsat_cases:
            self.assertFalse(dpll(case), f"Problem: {case}, expected UNSAT, returned SAT")
            self.assertIsNone(dpll_model(case), f"Problem: {case}, expected UNSAT, returned SAT")
    