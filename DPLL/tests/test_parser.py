from parser import Parser, Variable
from operators import *
from constants import Tautology, Contradiction

parser = Parser()
t = parser.parse("a\\/b")
assert (t.get_left().name == "a")
assert (t.get_right().name == "b")
assert (isinstance(t.get_root(), Disjunction))

t = parser.parse("a/\\b")
assert (t.get_left().name == "a")
assert (t.get_right().name == "b")
assert (isinstance(t.get_root(), Conjunction))

t = parser.parse("a->b")
assert (t.get_left().name == "a")
assert (t.get_right().name == "b")
assert (isinstance(t.get_root(), Implication))

t = parser.parse("a<->b")
assert (t.get_left().name == "a")
assert (t.get_right().name == "b")
assert (isinstance(t.get_root(), Equivalence))

t = parser.parse("¬a")
assert (t.get_left().name == "a")
assert (isinstance(t.get_root(), Negation))

t2 = parser.parse("((p <-> ~q) -> r) -> (r /\\~p /\\ (T \\/ F))")
assert(isinstance(t2.get_root(), Implication))
assert(isinstance(t2.get_left().get_root(), Implication))
assert(isinstance(t2.get_right().get_root(), Conjunction))
assert(isinstance(t2.get_left().get_left().get_root(), Equivalence))
assert(isinstance(t2.get_left().get_right(), Variable))
assert(t2.get_left().get_right().name == "r")
assert(isinstance(t2.get_left().get_left().get_left(), Variable))
assert(t2.get_left().get_left().get_left().name == "p")
assert(isinstance(t2.get_left().get_left().get_right().get_root(), Negation))
assert(isinstance(t2.get_left().get_left().get_right().get_left(), Variable))
assert(t2.get_left().get_left().get_right().get_left().name =="q")
assert(isinstance(t2.get_right().get_left().get_root(), Disjunction))
assert(isinstance(t2.get_right().get_left().get_left().get_root(), Conjunction))
assert(t2.get_right().get_left().get_left().get_left().name == "r")
assert(isinstance(t2.get_right().get_left().get_left().get_right().get_root(), Negation))
assert(t2.get_right().get_left().get_left().get_left().name == "r")
assert(isinstance(t2.get_right().get_right(), Tautology))
assert(isinstance(t2.get_right().get_left().get_right(), Contradiction))