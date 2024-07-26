import unittest
import pytest
from DPLL import pl_parser
from typing import List

parser = pl_parser.Parser
token = pl_parser.Token
tokentype = pl_parser.TokenType

var = tokentype.VARIABLE
bop = tokentype.BINARY_OPERATOR
uop = tokentype.UNARY_OPERATOR
lb = tokentype.START_BRACKET
rb = tokentype.END_BRACKET


class LexerTest(unittest.TestCase):

    def test_lexer_builders(self):
        self.assertTrue(isinstance(token.BinaryOp(""), token))
        self.assertEqual(token.BinaryOp("").type, bop)
        self.assertEqual(token.BinaryOp("abc").value, "abc")

        self.assertTrue(isinstance(token.UnaryOp(""), token))
        self.assertEqual(token.UnaryOp("").type, uop)
        self.assertEqual(token.UnaryOp("abc").value, "abc")

        self.assertTrue(isinstance(token.StartBracket(), token))
        self.assertEqual(token.StartBracket().type, lb)
        self.assertEqual(token.StartBracket().value, "(")

        self.assertTrue(isinstance(token.EndBracket(), token))
        self.assertEqual(token.EndBracket().type, rb)
        self.assertEqual(token.EndBracket().value, ")")

        self.assertTrue(isinstance(token.Var(""), token))
        self.assertEqual(token.Var("").type, var)
        self.assertEqual(token.Var("abc").value, "abc")

    def test_lexer(self):
        values = lambda l: [x.value for x in l]
        types = lambda l: [x.type for x in l]

        # Test basic cases
        test_case = parser.lexer("a")
        self.assertEqual(len(test_case), 1) 
        self.assertEqual(test_case[0].type, var)
        self.assertEqual(test_case[0].value, "a")

        test_case = parser.lexer("a b ")
        self.assertEqual(len(test_case), 1)
        self.assertEqual(test_case[0].type, var)
        self.assertEqual(test_case[0].value, "ab")
        
        test_case = parser.lexer("")
        self.assertEqual(len(test_case), 0)

        test_case = parser.lexer(" ")
        self.assertEqual(len(test_case), 0)

        test_case = parser.lexer("a -> b ")
        self.assertEqual(len(test_case), 3) 
        self.assertEqual(values(test_case), ["a", "→", "b"])
        self.assertEqual(types(test_case), [var, bop, var])

        test_case = parser.lexer("a -> b -> c ")
        self.assertEqual(len(test_case), 5)
        self.assertEqual(values(test_case), ["a", "→", "b", "→", "c"])
        self.assertEqual(types(test_case), [var, bop, var, bop, var])

        test_case = parser.lexer("a \\/ b")
        self.assertEqual(len(test_case), 3)
        self.assertEqual(values(test_case), ["a", "∨", "b"])
        self.assertEqual(types(test_case), [var, bop, var])

        test_case = parser.lexer("a /\\ b")
        self.assertEqual(len(test_case), 3)
        self.assertEqual(values(test_case), ["a", "∧", "b"])
        self.assertEqual(types(test_case), [var, bop, var])

        test_case = parser.lexer("a -> b")
        self.assertEqual(len(test_case), 3)
        self.assertEqual(values(test_case), ["a", "→", "b"])
        self.assertEqual(types(test_case), [var, bop, var])

        test_case = parser.lexer("a <-> b")
        self.assertEqual(len(test_case), 3)
        self.assertEqual(values(test_case), ["a", "↔", "b"])
        self.assertEqual(types(test_case), [var, bop, var])

        test_case = parser.lexer("¬a")
        self.assertEqual(len(test_case), 2)
        self.assertEqual(values(test_case), ["¬", "a"])
        self.assertEqual(types(test_case), [uop, var])

        bad_operators = ["a >> b", "a << b", "a <> b", "a ->> b", "a <<-> b"]
        for x in bad_operators:
            with self.assertRaises(SyntaxError):
                parser.lexer(x)

        test_case = parser.lexer("(a)")
        self.assertEqual(len(test_case), 3)
        self.assertEqual(values(test_case), ["(","a",")"])
        self.assertEqual(types(test_case), [lb, var, rb])

        test_case = parser.lexer("(aaa -> b) /\\ c")
        self.assertEqual(len(test_case), 7)
        self.assertEqual(values(test_case), ["(","aaa","→","b",")","∧","c"])
        self.assertEqual(types(test_case), [lb, var, bop, var, rb, bop, var])
    
    def test_syntax_check(self):
        test_cases = ["a","(a)",
                      "(a -> b)","(a \\/ b)","(a /\\ b)","(a <-> b)",
                      "¬a","¬¬a",
                      "¬(a<->b)","¬¬¬(a->b->c/\\d)<->(e\\/a)"
        ]
        for test_case in test_cases:
            self.assertTrue(parser.syntax_check(parser.lexer(test_case)))

        bad_test_cases = [""," ","()" # Empty cases
                          "(a ->)","(a","a <-> b)", "((a -> b) -> c))" # Mismatched brackets case
                          "a ¬ a", # Negation as binary operator
                          "\\/ a","/\\ a","-> a","<-> a", # Binary operators as prefix unary
                          "a \\/","a /\\","a ->","a <->", # Binary operators as postfix unary
                          "a n ¬b", # n should be treated as char not operator
                          "a v ¬b", # v should be treated as char not operator
                          "a(b && c)", # do not allow implicit distribution
                          "((a && b)", "(a && b))" # mismatched brackets
                          ] 
        for test_case in bad_test_cases:
            self.assertFalse(parser.syntax_check(parser.lexer(test_case)))
    
    def test_parser(self):
        pass