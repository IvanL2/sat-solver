import pytest
from DPLL.tree import Tree

# Unit test for tree
def test_tree_attrs():
  dut = Tree("None")
  assert hasattr(dut, "value")
  assert hasattr(dut, "left")
  assert hasattr(dut, "right")
  assert hasattr(dut, "parent")

  assert hasattr(dut, "get_height")
  assert callable(getattr(dut, "get_height"))

def test_tree_get_height():
  dut = Tree("AAAAAAA")
  with pytest.raises(TypeError):
    dut.get_height() == 1

  dut = Tree("AAAAA", left=Tree("BBBBB"), right=Tree("CCCCC"))
  assert Tree.get_height(dut) == 2