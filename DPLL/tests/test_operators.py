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
        from operators import Or
    except NameError:
        assert False

    connective = Or()
    assert connective.operator == "|"
    assert connective.is_connective == True

    try:
        from operators import And
    except NameError:
        assert False

    connective = And()
    assert connective.operator == "&"
    assert connective.is_connective == True

    try:
        from operators import Implies
    except NameError:
        assert False

    connective = Implies()
    assert connective.operator == ">"
    assert connective.is_connective == True


    try:
        from operators import Equiv
    except NameError:
        assert False

    connective = Equiv()
    assert connective.operator == "="
    assert connective.is_connective == True

    try:
        from operators import Not
    except NameError:
        assert False

    operator = Not()
    assert operator.operator == "!"
    assert operator.is_operator == True


