from dataclasses import dataclass, field
from dpll.types import Operator, Atom, Variable, Tautology, Contradiction
from typing import Callable, TypeVar


VariableName = str
LogicTreeValue = Operator | Atom
T = TypeVar("T")
U = TypeVar("U")


@dataclass(eq=False)
class LogicTree:
    value: LogicTreeValue
    literal: bool = field(init=False)
    left: "LogicTree | None" = None
    right: "LogicTree | None" = None

    def __post_init__(self: "LogicTree") -> None:
        if self.value is Operator.NEGATION:
            assert self.left is not None
            self.literal = type(self.left.value) is not Operator
        else:
            self.literal = type(self.value) is not Operator

    def __str__(self: "LogicTree", first: bool = True) -> str:
        match self.value:
            case Variable(name=name) | Tautology(name=name) | Contradiction(name=name):
                return name
            case Operator.NEGATION:
                left = "" if self.left is None else self.left.__str__(first=False)
                return "¬" + left
            case Operator(as_str):
                left = "" if self.left is None else self.left.__str__(first=False)
                right = "" if self.right is None else self.right.__str__(first=False)
                return "(" + left + as_str + right + ")"

    def __repr__(self):
        return self.__str__()

    def print_tree(self: "LogicTree", depth: int = 0):
        """Prints elements of a tree in preorder"""
        if depth == 0:
            print("format: node, depth")
        print(self.value, depth)
        if self.left is not None:
            self.left.print_tree(depth=depth + 1)
        if self.right:
            self.right.print_tree(depth=depth + 1)

    def _get_var_names(self: "LogicTree", names: set[str]):
        if isinstance(self.value, Variable):
            names.add(str(self.value))
            return
        if self.left is not None:
            self.left._get_var_names(names)
        if self.right is not None:
            self.right._get_var_names(names)

    def get_var_names(self: "LogicTree") -> set[str]:
        names: set[str] = set()
        self._get_var_names(names)
        return names

    def left_value_if_not_none(self: "LogicTree") -> None | LogicTreeValue:
        if self.left is not None:
            return self.left.value
        else:
            return None

    def right_value_if_not_none(self: "LogicTree") -> None | LogicTreeValue:
        if self.right is not None:
            return self.right.value
        else:
            return None

    @staticmethod
    def map_lr_if_not_none(
            method: Callable[["LogicTree"], "LogicTree"],
            tree: "LogicTree"
    ) -> tuple["LogicTree | None", "LogicTree | None"]:
        if tree.left is not None:
            left_tree = method(tree.left)
        else:
            left_tree = None
        if tree.right is not None:
            right_tree = method(tree.right)
        else:
            right_tree = None
        return left_tree, right_tree

    @staticmethod
    def check_node_children(tree: "LogicTree") -> bool:
        match tree.value:
            case Operator.NEGATION:
                return tree.left is not None and tree.right is None
            case Operator():
                return tree.left is not None and tree.right is not None
            case _:
                return tree.left is None and tree.right is None

    @staticmethod
    def check_node_children_and_raise(tree: "LogicTree") -> None:
        if not LogicTree.check_node_children(tree):
            raise ValueError(f"LogicTree node (value {str(tree.value)}) has invalid child \
                               (left none: {tree.left is None}, right none: {tree.right is None}")

    @staticmethod
    def validate_tree(tree: "LogicTree") -> bool:
        if LogicTree.check_node_children(tree):
            left_valid = tree.left is None or LogicTree.validate_tree(tree.left)
            right_valid = tree.right is None or LogicTree.validate_tree(tree.right)
            return left_valid and right_valid
        else:
            return False

    @staticmethod
    def validate_tree_and_raise(tree: "LogicTree") -> None:
        if not LogicTree.validate_tree(tree):
            raise ValueError(f"LogicTree contains illegal structures: {str(tree)}")
