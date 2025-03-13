try:
    from enum import StrEnum  # python >=3.11
except ImportError:
    from strenum import StrEnum  # python <3.11 (requires pip install)

from dataclasses import dataclass
from dpll.tree import Tree


class Semantics:
    def polarise(node: Tree, pol: int = 1) -> Tree:
        """Adds polarity information for sake of optimising definitional transforms"""
        node.pol = pol
        if isinstance(node.value, Operator):
            if node.value == Operator.CONJUNCTION or node.value == Operator.DISJUNCTION:
                Semantics.polarise(node.left, pol=pol)
                Semantics.polarise(node.right, pol=pol)
            elif node.value == Operator.NEGATION:
                Semantics.polarise(node.left, pol=-pol)
            elif node.value == Operator.IMPLICATION:
                Semantics.polarise(node.left, pol=-pol)
                Semantics.polarise(node.right, pol=pol)
            elif node.value == Operator.EQUIVALENCE:
                Semantics.polarise(node.left, pol=0)
                Semantics.polarise(node.right, pol=0)
        else:
            return None

    def literal_marker(ast: Tree):
        """Adds a field to each AST node, marking if the node represents a literal"""
        # If not a negation (must be disj)
        if isinstance(ast.value, Operator) and ast.value != Operator.NEGATION:
            ast.literal = False  # then clearly not a literal
        elif not isinstance(ast.value, Operator):  # If variable then clearly literal
            ast.literal = True
            return
        else:
            ast.literal = True
            return
        if ast.left is not None:
            Semantics.literal_marker(ast.left)
        if ast.right is not None:
            Semantics.literal_marker(ast.right)


@dataclass
class Variable:
    name: str
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

@dataclass
class Tautology:
    name: str = "⊤"
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()


@dataclass
class Contradiction:
    name: str = "⊥"
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()


Literal = Variable | Tautology | Contradiction


class Operator(StrEnum):
    NEGATION = "¬"
    CONJUNCTION = "&"
    DISJUNCTION = "|"
    IMPLICATION = ">"
    EQUIVALENCE = "="
