from .tree import Tree
class Semantics:
    def polarise(node : Tree, pol=1) -> Tree:
        if (node.value == "start"):
            Semantics.polarise(node.left)
            return
        node.pol = pol
        if node.value.name == "&" or node.value.name == "|":
            Semantics.polarise(node.left, pol=pol)
            Semantics.polarise(node.right, pol=pol)
        elif node.value.name == "!":
            Semantics.polarise(node.left, pol=-pol)
        elif node.value.name == ">":
            Semantics.polarise(node.left, pol=-pol)
            Semantics.polarise(node.right, pol=pol)
        elif node.value.name == "=":
            Semantics.polarise(node.left, pol=0)
            Semantics.polarise(node.right, pol=0)
        else:
            return None

    def literal_marker(ast: Tree):
        if ast.value == "start":
            Semantics.literal_marker(ast.left)
            return
        # If not a negation (is and, or, implies, equiv)
        if isinstance(ast.value, Connective) and ast.value.name != "!":
            ast.literal = False # then clearly not a literal
        elif not isinstance(ast.value, Operator):
            ast.literal = True
            return
        elif isinstance(ast.left.value, Operator) and ast.left.value.name == "!":
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

class Operator():
    def __init__(self, name):
        self.name = name
        self.is_operator = True
    
    def __str__(self):
        return f"<Operator {self.name}>"

    def Negation():
        return Operator("!")

class Connective(Operator):
    def __init__(self, name):
        super().__init__(name)
        self.is_connective = True
    
    def Conjunction():
        return Connective("&")
    def Disjunction():
        return Connective("|")
    def Implication():
        return Connective(">")
    def Equivalence():
        return Connective("=")