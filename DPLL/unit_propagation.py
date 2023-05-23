from tree import Tree
from parser import Parser

class Clause: # empty clause means unsat, empty SET of clauses means sat
    def __init__(self):
        self.disj = 0
        self.vars = []

class PositiveVariable:
    def __init__(self,name):
        self.name = name
        self.sign = 1

class NegativeVariable:
    def __init__(self,name):
        self.name = name
        self.sign = -1

class Unit_Propagation:

    def print_clause(clause : Clause):
        string = ""
        i = clause.disj
        for x in clause.vars:
            if isinstance(x, NegativeVariable):
                string+= "¬"+x.name
            else:
                string+=x.name
            if i > 0:
                string += "∨"
                i-=1
        print(string)
    
    def __init__(self):
        self.unique_variables = set()

    def propagate(self,clauses : set):
        clauseobjs = set()
        for x in clauses:
            new = Clause()
            self._convert_to_clause_object(x, new)
            clauseobjs.add(new)
        for x in clauseobjs:
            Unit_Propagation.print_clause(x)
        for var in self.unique_variables:
            if len(clauseobjs) == 0:
                return SAT
            print(len(clauseobjs))
            for c in clauseobjs.copy():
                if var in [x for x in c.vars]: # if var is part of variable list
                    clauseobjs.remove(c)
                negativeVar = NegativeVariable(var.name)
                negativeVar.sign = -var.sign
                for i in c.vars:
                    if i.name == negativeVar.name and i.sign == negativeVar.sign:
                        c.vars.remove(i)
                        c.disj-=1
        if len(clauseobjs) == 0:
            return SAT
        else:
            return UNSAT

    def _convert_to_clause_object(self,clause : Tree, obj : Clause):

        if isinstance(clause.get_root(), Negation):
            if clause.get_left().get_root().name not in [x.name and isinstance(x,NegativeVariable) for x in self.unique_variables]:
                var = NegativeVariable(clause.get_left().get_root().name)
                self.unique_variables.add(var)
                obj.vars.append(var)
            else:
                var = [x.name and isinstance(x,NegativeVariable) for x in self.unique_variables][0]
                obj.vars.append(var)
        elif isinstance(clause.get_root(), Disjunction):
            obj.disj+=1
            self._convert_to_clause_object(clause.get_left(), obj)
            self._convert_to_clause_object(clause.get_right(), obj)
        else: # var
            if clause.get_root().name not in [x.name and isinstance(x,PositiveVariable) for x in self.unique_variables]:
                var = PositiveVariable(clause.get_root().name)
                self.unique_variables.add(var)
                obj.vars.append(var)
            else:
                var = [x.name and isinstance(x,PositiveVariable) for x in self.unique_variables][0]
                self.unique_variables.add(var)
                obj.vars.append(var)
                
