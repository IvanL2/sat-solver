from dataclasses import dataclass
from typing import Optional, Any
@dataclass(eq=False)
class Tree:
    value: Any
    left: Optional['Tree'] = None
    right: Optional['Tree'] = None
    pol: Optional[int] = None
    literal: Optional[bool] = None

    def __str__(tree: "Tree", first: bool = True):
        if tree is None:
            return ""
        if str(tree.value) in ["¬","&","|",">","="]:
            if str(tree.value) == "¬":
                left = "" if tree.left is None else tree.left.__str__(first=False)
                return "¬" + left
            else:
                left = "" if tree.left is None else tree.left.__str__(first=False)
                right = "" if tree.right is None else tree.right.__str__(first=False)
                return "(" + left + str(tree.value) + right + ")"
        else:
            return str(tree.value)

    def __repr__(self):
        return self.__str__()

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