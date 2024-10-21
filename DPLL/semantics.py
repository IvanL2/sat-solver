from .tree import Tree
from enum import Enum

class Semantics:
    def polarise(node : Tree, pol=1) -> Tree:
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
        # If not a negation (is and, or, implies, equiv)
        if isinstance(ast.value, Operator) and ast.value != Operator.NEGATION:
            ast.literal = False # then clearly not a literal
        elif not isinstance(ast.value, Operator):
            ast.literal = True
            return
        elif isinstance(ast.left.value, Operator) and ast.left.value == Operator.NEGATION:
            ast.literal = False
        else:
            ast.literal = True
            return
        if ast.left != None:
            Semantics.literal_marker(ast.left)
        if ast.right != None:
            Semantics.literal_marker(ast.right)


class Variable():
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"<Variable {self.name}>"

class Tautology(Variable):
    def __init__(self):
        super().__init__("⊤")

class Contradiction(Variable):
    def __init__(self):
        super().__init__("⊥")

class Operator(Enum):
    NEGATION = 0
    CONJUNCTION = 1
    DISJUNCTION = 2
    IMPLICATION = 3
    EQUIVALENCE = 4

    def __str__(self):
        match (self):
            case Operator.NEGATION:
                return "¬"
            case Operator.CONJUNCTION:
                return "&"
            case Operator.DISJUNCTION:
                return "|"
            case Operator.IMPLICATION:
                return ">"
            case Operator.EQUIVALENCE:
                return "="
        