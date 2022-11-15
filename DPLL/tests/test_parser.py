from parser import Parser
from operators import *

parser = Parser()
t = parser.parse("a\/b")
assert (t.get_left() == "a")
assert (t.get_right() == "b")
assert (isinstance(t.get_root(), Disjunction))