import os
import pytest

def test_operators():
    try:
        from operators import Connective
    except ImportError:
        assert False

    connective = Connective()
    assert connective.operator == None
    assert connective.is_connective == True

    try:
        from operators import Disjunction
    except NameError:
        assert False

    connective = Disjunction()
    assert connective.operator == "|"
    assert connective.is_connective == True

    try:
        from operators import Conjunction
    except NameError:
        assert False

    connective = Conjunction()
    assert connective.operator == "&"
    assert connective.is_connective == True

    try:
        from operators import Implication
    except NameError:
        assert False

    connective = Implication()
    assert connective.operator == ">"
    assert connective.is_connective == True


    try:
        from operators import Equivalence
    except NameError:
        assert False

    connective = Equivalence()
    assert connective.operator == "="
    assert connective.is_connective == True

    try:
        from operators import Negation
    except NameError:
        assert False

    operator = Negation()
    assert operator.operator == "!"
    assert operator.is_operator == True


