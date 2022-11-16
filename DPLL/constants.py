class Constant:
    def __init__(self):
        self.is_constant = True

class Tautology(Constant):
    def __init__(self):
        self.name = "⊤"

class Contradiction(Constant):
    def __init__(self):
        self.name = "⊥"

class SAT(Constant):
    pass

class UNSAT(Constant):
    pass