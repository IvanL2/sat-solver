from tree import Tree
from parser import Variable
from constants import *
from cnf_transformer import Polarity

class Pure_Eliminator:
    
    def __init__(self):
        self._vars = set()

    def eliminate(self, clauses : set) -> set:
        # step 1: find identify pure literals
        # step 2: remove variables containing pure literals
        for clause in clauses.copy():
            Polarity.polarise(clause)
            if isinstance(clause, Contradiction):
                return UNSAT
            if self._is_tautology_in_tree(clause): # remove clauses with T
                clauses.remove(clause)
            self._classify_variables(clause)
        pure = set()
        for var in self._vars:
            if (var[0], -var[1]) not in self._vars:
                pure.add((var[0], var[1]))
        for p in pure:
            for clause in clauses.copy():
                if self._tree_has_variable(clause, p[0]):
                    clauses.remove(clause)

    def _is_tautology_in_tree(self,tree):
        if isinstance(tree, Tautology):
            return True
        elif isinstance(tree, Variable) or isinstance(tree, Contradiction):
            return False
        else:
            if isinstance(tree, Tree):
                return self._is_tautology_in_tree(tree.get_left()) or self._is_tautology_in_tree(tree.get_right())
    
    def _tree_has_variable(self, tree, var):
        if isinstance(tree, Tree):
            return self._tree_has_variable(tree.get_left(), var) or self._tree_has_variable(tree.get_right(), var)
        elif isinstance(tree, Variable):
            return var == tree.name
            

    def _classify_variables(self, tree):
        if (tree == None):
            return None
        if isinstance(tree, Variable) or isinstance(tree, Constant):
            self._vars.add((tree.name,tree.pol))
        else:
            self._classify_variables(tree.get_left())
            self._classify_variables(tree.get_right())

