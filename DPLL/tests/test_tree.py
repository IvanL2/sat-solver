import pytest
from exceptions import NodeException
from exceptions import RootException
from operators import Operator
try:
    from tree import Tree
except:
    assert False



try:
    tree = Tree()
except:
    assert False

tree.set_root("a")
assert tree.get_root() == "a"
assert tree.get_root() != None

with pytest.raises(NodeException):
    tree.set_nodes("a","b")


tree.set_root(Operator())
tree.set_nodes("a","b")
assert tree.get_left() == "a"
assert tree.get_right() == "b"

with pytest.raises(RootException):
    tree.set_root(Tree())

tree1 = tree()
tree2 = tree()
tree.set_nodes(tree1, tree2)
assert tree.get_left() == tree1
assert tree.get_right() == tree2
assert tree.get_left() != tree1
assert tree.get_right() != tree2


tree.set_left("test")
assert tree.get_left == "test"
tree.set_right("test")
assert tree.get_right == "test"