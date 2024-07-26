from .semantics import *
from .pl_parser import Parser
from .tree import Tree
from . import verbosity_config
from typing import Set, List, Tuple
import copy

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

    def transform_to_variables(tree: Tree, verbose: bool=False) -> Set[Tuple[str, bool]]:
        internal_verbose = verbosity_config.SOLVER_LITERAL_PARSING_VERBOSE
        Semantics.literal_marker(tree)
        tree_literals = Solver.get_literals(tree)
        if internal_verbose:
            print(f"Literals of {Parser.print_exp_return_str(tree)}:", " ".join([Parser.print_exp_return_str(x) for x in tree_literals]))
        vars = set()
        for x in tree_literals:
            if isinstance(x.value, Operator): # At this point, only operator is negation
                vars.add((x.left.value.name, False))
            else:
                vars.add((x.value.name, True))
        return vars
    
    
    def propagate(clauses: list, verbose: bool=False):
        internal_verbose = verbose and verbosity_config.SOLVER_UNIT_PROPAGATION_VERBOSE
        unit_clauses = list(filter(lambda c: len(c)==1, clauses))
        model = []
        if internal_verbose: print(f"Start propagation, unit clauses: {unit_clauses}\nStarting clauses:")
        while (len(unit_clauses) > 0):
            var = next(iter(unit_clauses[0]))
            model.append(var)
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
            if internal_verbose: print(f"End propagation round, new clauses: {clauses}\n")
            unit_clauses = list(filter(lambda c: len(c)==1, clauses))
        return model


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
                elif (y[0] == "⊤" and y[1] == True) or (y[0] == "⊥" and y[1] == False):
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
                if (y[0] == "⊥" and y[1] == True) or (y[0] == "⊤" and y[1] == False):
                    if (verbose and verbosity_config.SOLVER_CONTRA_REMOVE_VERBOSE):
                        print(f"Removing contradiction {y} from clause {x}.")
                    x.remove(y)
                    break
    
    def get_unique_names(clauses: list) -> Set[str]:
        uniques = set()
        for x in clauses:
            for y in x:
                try:
                    uniques.add((y[0], y[1]))
                except Exception:
                    raise RuntimeError()
        return uniques
    
    def dpll(clauses: list, verbose: bool=False, depth: int=0) -> Tuple[bool, List[Tuple[str, bool]]]:
        iteration_verbose = verbose and verbosity_config.SOLVER_ITERATION_SUMMARY_VERBOSE
        unique_var_names = Solver.get_unique_names(clauses)
        model = []
        model += Solver.pure_literal_elim(clauses, unique_var_names, verbose=verbose)
        model += Solver.taut_elim(clauses, verbose=verbose)
        model += Solver.propagate(clauses, verbose=verbose)
    
        if len(clauses) == 0:
            if iteration_verbose: print(f"Empty set of clauses, SAT at depth {depth}")
            ret_val = (True, model)
            return ret_val
        elif set() in clauses:
            if iteration_verbose: print(f"Empty clause found, UNSAT at depth {depth}")
            ret_val = (False, None)
            return ret_val

        unique_var_names = Solver.get_unique_names(clauses)

        var = next(iter(unique_var_names))
        clauses_with_not_var = copy.deepcopy(clauses)
        not_var = (var[0], not var[1])
        newset = set()
        newset.add(var)
        clauses.append(newset)
        newset = set()
        newset.add(not_var)
        clauses_with_not_var.append(newset)
        (satisfiable, new_model) = Solver.dpll(clauses, verbose=verbose, depth=depth+1)
        if (satisfiable):
            if iteration_verbose:
                print(f"First branch returned SAT, append model at depth {depth}")
            model += new_model
            return (True, model)
        else:
            if iteration_verbose:
                print(f"\nFirst branch returned UNSAT, current depth {depth}, try {clauses_with_not_var}")
            (satisfiable2, new_model_2) = Solver.dpll(clauses_with_not_var, verbose=verbose, depth=depth+1)
            if (satisfiable2 == False):
                if iteration_verbose: print(f"\nSecond branch returned UNSAT, current depth {depth}")
                return (False, None)
            else:
                if iteration_verbose: print(f"\nSecond branch returned SAT, append model at depth {depth}")
                model += new_model_2
                return (True, model)

    def solve(old_clauses: Set[Tree], verbose: bool=False) -> Tuple[bool, List[Tuple[str, bool]]]:
        """Returns a tuple in the form (True/False if Satisfiable/Unsat, [list of variables that form the model if sat, else None])"""
        clauses = list()
        for x in old_clauses:
            vars = Solver.transform_to_variables(x, verbose=verbose)
            clauses.append(vars)
        Solver.contra_elim(clauses, verbose=verbose) # Didn't check for Bottom in parser/transformer, so do it now.
        return Solver.dpll(clauses, verbose=verbose)
