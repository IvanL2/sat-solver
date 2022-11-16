def test_constant():
    try:
        from constants import Tautology
    except:
        assert False
    t = Tautology()
    assert hasattr(t,"name")
    assert (t.name == "⊤")

    try:
        from constants import Contradiction
    except:
        assert False
    t = Contradiction()
    assert hasattr(t,"name")
    assert (t.name == "⊥")

    try:
        from constants import SAT
    except:
        assert False
    
    try:
        from constants import UNSAT
    except:
        assert False