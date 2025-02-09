import pytest
from dpll.parser import Token as token
from dpll.parser import Parser as parser
from dpll.parser import TokenType

var = TokenType.LITERAL
bop = TokenType.BINARY_OPERATOR
uop = TokenType.UNARY_OPERATOR
lb = TokenType.START_BRACKET
rb = TokenType.END_BRACKET


def test_lexer_builders():
    assert isinstance(token.BinaryOp(""), token)
    assert token.BinaryOp("").type == bop
    assert token.BinaryOp("abc").value == "abc"

    assert isinstance(token.UnaryOp(""), token)
    assert token.UnaryOp("").type == uop
    assert token.UnaryOp("abc").value == "abc"

    assert isinstance(token.StartBracket(), token)
    assert token.StartBracket().type == lb
    assert token.StartBracket().value == "("

    assert isinstance(token.EndBracket(), token)
    assert token.EndBracket().type == rb
    assert token.EndBracket().value == ")"

    assert isinstance(token.Var(""), token)
    assert token.Var("").type == var
    assert token.Var("abc").value == "abc"


def test_lexer():

    def values(arr_of_tokens: list[token]):
        return [x.value for x in arr_of_tokens]

    def types(arr_of_tokens: list[token]):
        return [x.type for x in arr_of_tokens]

    # Test basic cases
    test_case = parser.lexer("a")
    assert len(test_case) == 1
    assert test_case[0].type == var
    assert test_case[0].value == "a"

    test_case = parser.lexer("a b ")
    assert len(test_case) == 1
    assert test_case[0].type == var
    assert test_case[0].value == "ab"

    test_case = parser.lexer("")
    assert len(test_case) == 0

    test_case = parser.lexer(" ")
    assert len(test_case) == 0

    test_case = parser.lexer("a -> b ")
    assert len(test_case) == 3
    assert values(test_case) == ["a", "→", "b"]
    assert types(test_case) == [var, bop, var]

    test_case = parser.lexer("a -> b -> c ")
    assert len(test_case) == 5
    assert values(test_case) == ["a", "→", "b", "→", "c"]
    assert types(test_case) == [var, bop, var, bop, var]

    test_case = parser.lexer("a \\/ b")
    assert len(test_case) == 3
    assert values(test_case) == ["a", "∨", "b"]
    assert types(test_case) == [var, bop, var]

    test_case = parser.lexer("a /\\ b")
    assert len(test_case) == 3
    assert values(test_case) == ["a", "∧", "b"]
    assert types(test_case) == [var, bop, var]

    test_case = parser.lexer("a -> b")
    assert len(test_case) == 3
    assert values(test_case) == ["a", "→", "b"]
    assert types(test_case) == [var, bop, var]

    test_case = parser.lexer("a <-> b")
    assert len(test_case) == 3
    assert values(test_case) == ["a", "↔", "b"]
    assert types(test_case) == [var, bop, var]

    test_case = parser.lexer("¬a")
    assert len(test_case) == 2
    assert values(test_case) == ["¬", "a"]
    assert types(test_case) == [uop, var]

    bad_operators = ["a >> b", "a << b", "a <> b", "a ->> b", "a <<-> b"]
    for x in bad_operators:
        with pytest.raises(SyntaxError):
            parser.lexer(x)

    test_case = parser.lexer("(a)")
    assert len(test_case) == 3
    assert values(test_case) == ["(", "a", ")"]
    assert types(test_case) == [lb, var, rb]

    test_case = parser.lexer("(aaa -> b) /\\ c")
    assert len(test_case) == 7
    assert values(test_case) == ["(", "aaa", "→", "b", ")", "∧", "c"]
    assert types(test_case) == [lb, var, bop, var, rb, bop, var]


def test_syntax_check():
    test_cases = ["a", "(a)",
                  "(a -> b)", "(a \\/ b)", "(a /\\ b)", "(a <-> b)",
                  "¬a", "¬¬a",
                  "¬(a<->b)", "¬¬¬(a->b->c/\\d)<->(e\\/a)"]

    for test_case in test_cases:
        assert parser.syntax_check(parser.lexer(test_case))

    bad_test_cases = ["", " ", "()"  # Empty cases
                      "(a ->)", "(a", "a <-> b)", "((a -> b) -> c))"  # Mismatched brackets case
                      "a ¬ a",  # Negation as binary operator
                      "\\/ a", "/\\ a", "-> a", "<-> a",  # Binary operators as prefix unary
                      "a \\/", "a /\\", "a ->", "a <->",  # Binary operators as postfix unary
                      "a n ¬b",  # n should be treated as char not operator
                      "a v ¬b",  # v should be treated as char not operator
                      "a(b && c)",  # do not allow implicit distribution
                      "((a && b)", "(a && b))"]  # mismatched brackets

    for test_case in bad_test_cases:
        assert parser.syntax_check(parser.lexer(test_case)) is False


def test_parser():
    pass
