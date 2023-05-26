from semantics import *
from parser import Parser
from tree import Tree
from typing import Set, List, Tuple

class Solver:

    def print_tree_with_literal(tree : Tree, depth=0):
        if (depth==0):
            print("format: node, depth")
        if (tree == None):
            return
        if (tree.value == "start"):
            print("start",0)
        else:
            print(tree.value.name, depth, "n/a" if not hasattr(tree, "literal") else "yes" if tree.literal else "no")
        if (isinstance(tree.value, Variable) and not isinstance(tree.value, Operator)):
            return
        Solver.print_tree_with_literal(tree.left, depth + 1)
        Solver.print_tree_with_literal(tree.right, depth + 1)
        

    def get_literals(tree: Tree) -> List[Tree]:
        literals = []
        if tree.literal:
            literals.append(tree)
            return literals
        if tree.left != None:
            literals += (Solver.get_literals(tree.left))
        if tree.right != None:
            literals += (Solver.get_literals(tree.right))
        return literals

    def transform_to_variables(tree: Tree) -> Set[Tuple[str, bool]]:
        Semantics.literal_marker(tree)
        tree_literals = Solver.get_literals(tree)
        vars = set()
        for x in tree_literals:
            if isinstance(x.value, Operator):
                vars.add((x.left.value.name, False))
            else:
                vars.add((x.value.name, True))
        return vars
    
    def propagate(clauses: list, var: Tuple[str, bool]):
        to_remove = []
        for c in clauses:
            if var in c:
                to_remove.append(c)
            for y in c:
                if (var[0], not var[1]) == y:
                    c.remove(y)
                    break
        for v in to_remove:
            clauses.remove(v)


    def pure_literal_elim(clauses: list, unique_var_names: set):
        pure_literals = []
        for var in unique_var_names:
            clauses_as_list = [list(clause) for clause in clauses] # clause is a set
            positive_occurences = list(filter(lambda x: x[1] == True and x[0]==var[0], [variable for c in clauses_as_list for variable in c]))
            negative_occurences = list(filter(lambda x: x[1] == False and x[0]==var[0], [variable for c in clauses_as_list for variable in c]))
            if len(positive_occurences) == 0 and len(negative_occurences):
                # Variable not in list
                continue
            if len(positive_occurences) == 0 or len(negative_occurences) == 0:
                # Pure literal
                pure_literals.append(var)
                continue

        to_remove = []
        for pure in pure_literals:
            for x in clauses:
                for y in x:
                    if y[0] == pure:
                       to_remove.append(x)
                       break
        for x in to_remove:
            clauses.remove(x)

    def taut_elim(clauses: list):
        to_remove = []
        for x in clauses:
            for y in x:
                if (y[0], not y[1]) in x:
                    to_remove.append(x)
                    break
                elif y[0] == "T":
                    to_remove.append(x)
                    break
        for x in to_remove:
            clauses.remove(x)
    
    def contra_elim(clauses: list):
        for x in clauses:
            for y in x:
                if y[0] == "F":
                    x.remove(y)
                    break
    
    def get_unique_names(clauses: list) -> Set[str]:
        uniques = set()
        for x in clauses:
            for y in x:
                try:
                    uniques.add((y[0], y[1]))
                except Exception:
                    print(y)
                    raise RuntimeError()
        return uniques

    def solve(old_clauses) -> Tuple[bool, List[Tuple[str, bool]]]:
        """Returns a tuple in the form (True/False if Satisfiable/Unsat, [list of variables that form the model if sat, else None])"""
        clauses = list()
        for x in old_clauses:
            vars = Solver.transform_to_variables(x)
            clauses.append(vars)
        Solver.contra_elim(clauses) # Didn't check for Bottom in parser/transformer, so do it now.
        model = []
        while True:
            unique_var_names = Solver.get_unique_names(clauses)
            if len(unique_var_names) == 0:
                break
            Solver.pure_literal_elim(clauses, unique_var_names)
            Solver.taut_elim(clauses)
            unit_clauses = list(filter(lambda c: len(c)==1, clauses))
            if len(unit_clauses) > 0:
                # Propagate unit clause
                var = next(iter(unit_clauses[0]))
                model.append(var)
                Solver.propagate(clauses, var)
            else:
                var = next(iter(unique_var_names))
                model.append(var)
                newset = set()
                newset.add(var)
                clauses.append(newset)
                Solver.propagate(clauses, var)
            if set() in clauses:
                return (False, None)
        return (len(clauses) == 0, None if len(clauses) != 0 else model)