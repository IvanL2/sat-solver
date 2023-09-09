from .semantics import *
from .pl_parser import Parser
from .tree import Tree
from . import verbosity_config
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
    
    def propagate(clauses: list, var: Tuple[str, bool], verbose: bool=False):
        internal_verbose = verbose and verbosity_config.SOLVER_UNIT_PROPAGATION_VERBOSE
        if internal_verbose: print("Propagating variable:", var)
        to_remove = []
        for c in clauses:
            if var in c:
                to_remove.append(c)
            for y in c:
                if (var[0], not var[1]) == y:
                    if internal_verbose: print(f"Found ({var[0], not var[1]}) in c; removing literal from clause {c}!")
                    c.remove(y)
                    break
        for v in to_remove:
            if internal_verbose: print(f"Removing clause {v}, from list of clauses!")
            clauses.remove(v)
        if internal_verbose: print("End propagation round")


    def pure_literal_elim(clauses: list, unique_var_names: set, verbose: bool=False) -> List[Tuple[str, bool]]:
        internal_verbose = verbose and verbosity_config.SOLVER_PURE_LITERAL_VERBOSE
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
        if internal_verbose: print("Pure literals:", pure_literals)
        for pure in pure_literals:
            for x in clauses:
                for y in x:
                    if y == pure:
                       if internal_verbose: print(f"Replaced {pure} in {x} with T")
                       x.remove(pure)
                       x.add(("T", True))
                       break
        return pure_literals

    def taut_elim(clauses: list, verbose: bool=False) -> List[Tuple[str, bool]]:
        internal_verbose = verbose and verbosity_config.SOLVER_TAUTOLOGY_REMOVE_VERBOSE
        to_remove = []
        for x in clauses:
            for y in x:
                if (y[0], not y[1]) in x:
                    to_remove.append(x)
                    break
                elif y[0] == "T":
                    to_remove.append(x)
                    break
        if internal_verbose: print("Tautologies:", to_remove)
        for x in to_remove:
            if internal_verbose: print("Removed tautology:", x)
            clauses.remove(x)
        return to_remove
    
    def contra_elim(clauses: list, verbose: bool=False):
        for x in clauses:
            for y in x:
                if y[0] == "F":
                    if (verbose):
                        print(f"Removing {y} from clause {x}.")
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

    def solve(old_clauses, verbose: bool=False) -> Tuple[bool, List[Tuple[str, bool]]]:
        """Returns a tuple in the form (True/False if Satisfiable/Unsat, [list of variables that form the model if sat, else None])"""
        clauses = list()
        for x in old_clauses:
            vars = Solver.transform_to_variables(x)
            clauses.append(vars)
        if (verbosity_config.SOLVER_CONTRA_REMOVE_VERBOSE and verbose):
            print("Removing contradictions before running DPLL algorithm.")
        Solver.contra_elim(clauses, verbose=(verbose and verbosity_config.SOLVER_CONTRA_REMOVE_VERBOSE)) # Didn't check for Bottom in parser/transformer, so do it now.
        if (verbosity_config.SOLVER_CONTRA_REMOVE_VERBOSE and verbose):
            print("Finished removing contradictions.")
        model = []
        summary_verbose = verbose and verbosity_config.SOLVER_ITERATION_SUMMARY_VERBOSE
        if verbose:
            print("Solver original list of clauses:\n","\n".join([str(x) for x in clauses]))
            print("Solver starting\n\n")
        while True:
            unique_var_names = Solver.get_unique_names(clauses)
            if len(unique_var_names) == 0:
                break
            model += [list(x) for x in Solver.pure_literal_elim(clauses, unique_var_names, verbose)]
            model += [list(x) for x in Solver.taut_elim(clauses, verbose)]
            unit_clauses = list(filter(lambda c: len(c)==1, clauses))
            if len(unit_clauses) > 0:
                # Propagate unit clause
                var = next(iter(unit_clauses[0]))
                model.append(var)
                Solver.propagate(clauses, var, verbose)
            else:
                var = next(iter(unique_var_names))
                if summary_verbose: print("Add", var,"to list of clauses.")
                model.append(var)
                newset = set()
                newset.add(var)
                clauses.append(newset)
                Solver.propagate(clauses, var, verbose)
            if set() in clauses:
                if summary_verbose:
                    print("Empty clause found in list of clauses (unsatisfiable): {"," ".join([str(x) for x in clauses]), "}")
                return (False, None)
            if summary_verbose:
                print("Solver iteration done. Remaining clauses:"," ".join([str(x) for x in clauses]))
                print("\n\n")
        if verbose: print("List of clauses empty. Satisfiable.")
        return (len(clauses) == 0, None if len(clauses) != 0 else model)