class Operator():
    def __init__(self):
        self.is_operator = True

class Connective(Operator):
    def __init__(self):
        super().__init__()
        self.operator = None
        self.is_connective = True

class Conjunction(Connective):
    def __init__(self):
        super().__init__()
        self.operator = "&"
    
class Disjunction(Connective):
    def __init__(self):
        super().__init__()
        self.operator = "|"

class Negation(Operator):
    def __init__(self):
        super().__init__()
        self.operator = "!"

class Implication(Connective):
    def __init__(self):
        super().__init__()
        self.operator = ">"

class Equivalence(Connective):
    def __init__(self):
        super().__init__()
        self.operator = "="