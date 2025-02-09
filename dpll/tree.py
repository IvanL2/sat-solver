from dataclasses import dataclass
from typing import Optional, Any

@dataclass(eq=False)
class Tree:
    value: Any
    left: Optional['Tree'] = None
    right: Optional['Tree'] = None
    pol: Optional[int] = None
    literal: Optional[bool] = None

    # __slots__ = ("value", "left", "right", "literal", "pol")

    # """Typical tree data structure, with parent information"""

    # def __init__(self, value, left: "Tree" = None, right: "Tree" = None, pol: int = None, literal: bool = False):
    #     self.left = left
    #     if self.left is not None:
    #         self.left.parent = self
    #     self.right = right
    #     if self.right is not None:
    #         self.right.parent = self
    #     self.value = value
    #     self.pol = pol
    #     self.literal = literal

    # def __deepcopy__(self: "Tree", memo) -> "Tree":
    #     left_tree = None
    #     right_tree = None
    #     if (self.left is not None):
    #         left_tree = self.left.__deepcopy__(memo)
    #     if (self.right is not None):
    #         right_tree = self.right.__deepcopy__(memo)
    #     new_tree = Tree(self.value, parent=self.parent, left=left_tree, right=right_tree)
    #     if hasattr(new_tree, "literal"):
    #         new_tree.literal = self.literal
    #     if hasattr(new_tree, "pol"):
    #         new_tree.pol = self.pol
    #     return new_tree