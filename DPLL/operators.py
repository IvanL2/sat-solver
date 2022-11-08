class Operator():
    def __init__(self):
        self.is_operator = True

class Connective(Operator):
    def __init__(self):
        super().__init__()
        self.operator = None;
        self.is_connective = True;

class And(Connective):
    def __init__(self):
        super().__init__()
        self.operator = "&";
    
class Or(Connective):
    def __init__(self):
        super().__init__()
        self.operator = "|";

class Not(Operator):
    def __init__(self):
        super().__init__()
        self.operator = "!"

class Implies(Connective):
    def __init__(self):
        super().__init__()
        self.operator = ">"

class Equiv(Connective):
    def __init__(self):
        super().__init__()
        self.operator = "="
    

    
