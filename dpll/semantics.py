from dpll.logic_tree import LogicTree
from dpll.types import Variable, Operator, Tautology, Contradiction


class Semantics:

    @staticmethod
    def polarise(node: LogicTree | None, pol: int = 1) -> None:
        """Adds polarity information for sake of optimising definitional transforms"""
        if node is None:
            return None
        node.pol = pol
        match node.value:
            case Operator.CONJUNCTION | Operator.DISJUNCTION:
                Semantics.polarise(node.left, pol=pol)
                Semantics.polarise(node.right, pol=pol)
            case Operator.NEGATION:
                Semantics.polarise(node.left, pol=-pol)
            case Operator.EQUIVALENCE:
                Semantics.polarise(node.left, pol=0)
                Semantics.polarise(node.right, pol=0)
            case _:
                return None

    @staticmethod
    def literal_marker(ast: LogicTree | None, assume_cnf: bool = True):
        """Adds a field to each AST node, marking if the node represents a literal"""
        if ast is None:
            return None
        match ast.value:
            case Operator.NEGATION:
                if assume_cnf:
                    ast.literal = True
                    return
                if ast.left is None:
                    raise RuntimeError("impossible case; negation cannot be empty")
                ast.literal = not isinstance(ast.left.value, Operator)  # is var
            case Variable(_) | Tautology(_) | Contradiction(_):
                ast.literal = True
                return
            case _:
                ast.literal = False
        if ast.left is not None:
            Semantics.literal_marker(ast.left)
        if ast.right is not None:
            Semantics.literal_marker(ast.right)
