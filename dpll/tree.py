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
        if str(tree.value) in ["¬", "&", "|", ">", "="]:
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
