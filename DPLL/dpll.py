from cnf_transformer import Transformer
from parser import Parser
from tree import Tree

p = Parser()
parsed = p.parse("((p <-> ~q) -> r) -> r /\~p")
assert isinstance(parsed, Tree)
print(p.print_tree(parsed,0))
t = Transformer()
clauses = t.transform(parsed)

for x in clauses:
    p.print_tree(x,0)