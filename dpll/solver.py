import copy
from typing import Set, List, NamedTuple, Tuple

from dpll.semantics import Semantics, Variable, Operator
from dpll.parser import Parser
from dpll.tree import Tree
import dpll.verbosity_config as verbosity_config


class SolverVariable(NamedTuple):
    """Dually used to represent a literal and its assignment in the model"""
    name: str
    polarity: bool

    def __str__(self):
        return f"({self.name}={'T' if (self.polarity) else 'F'})"

    def __repr__(self):
        return self.__str__()


class SolverResult(NamedTuple):
    """For sake of readability at top-level, name the fields"""
    satisfiable: bool
    model: List[SolverVariable]


SolverClause = set[SolverVariable]


class Solver:
    """Implements (a naive version) of the DPLL algorithm"""

    def print_tree_with_literal(tree: Tree, depth: int = 0):
        """Takes an AST from the transformer"""
        if depth == 0:
            print("format: node, depth")
        if tree is None:
            return
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
        if tree.left is not None:
            literals += (Solver.get_literals(tree.left))
        if tree.right is not None:
            literals += (Solver.get_literals(tree.right))
        return literals

    def transform_to_variables(tree: Tree, verbose: bool = False) -> Set[SolverVariable]:
        """Takes abstract syntax tree from previous steps; now in CNF so just split into tuples"""
        Semantics.literal_marker(tree)  # Depth-first search of a tree, marking the top node of a literal
        tree_literals = Solver.get_literals(tree)  # Collect
        if verbose:
            print(f"Literals of {Parser.print_exp_return_str(tree)}:", " ".join([Parser.print_exp_return_str(x) for x in tree_literals]))
        vars = SolverClause()
        for x in tree_literals:
            if isinstance(x.value, Operator):  # At this point, only operator is negation
                vars.add(SolverVariable(x.left.value.name, False))
            else:
                vars.add(SolverVariable(x.value.name, True))
        return vars

    def propagate(clauses: list) -> Tuple[List[SolverClause], List[SolverVariable]]:
        """DPLL unit propagation """
        new_clauses = copy.deepcopy(clauses)

        unit_clauses = list(filter(lambda c: len(c) == 1, new_clauses))
        model = []

        while (len(unit_clauses) > 0):
            var = next(iter(unit_clauses[0]))
            model.append(var)

            to_remove = []
            for c in new_clauses:
                if var in c:
                    to_remove.append(c)
                for y in c:
                    if (var[0], not var[1]) == y:
                        c.remove(y)
                        break
            for v in to_remove:
                new_clauses.remove(v)

            unit_clauses = list(filter(lambda c: len(c) == 1, new_clauses))
        return (new_clauses, model)

    def pure_literal_elim(clauses: List[SolverClause], unique_var_names: set) -> List[SolverVariable]:
        pure_literals = []
        for var in unique_var_names:
            clauses_as_list = [list(clause) for clause in clauses]  # clause is a set
            positive_occurences = list(filter(lambda x: x[1] is True and x[0] == var[0], [variable for c in clauses_as_list for variable in c]))
            negative_occurences = list(filter(lambda x: x[1] is False and x[0] == var[0], [variable for c in clauses_as_list for variable in c]))
            if len(positive_occurences) == 0 and len(negative_occurences) == 0:
                # Variable not in list
                continue
            if len(positive_occurences) == 0 or len(negative_occurences) == 0:
                # Pure literal (no +ve only -ve, or vice versa)
                pure_literals.append(var)
                continue
        for pure in pure_literals:
            for x in clauses:
                for y in x:
                    if y == pure:
                        x.remove(pure)
                        x.add(SolverVariable("⊤", True))
                        break
        return pure_literals

    def taut_elim(clauses: list) -> List[SolverVariable]:
        to_remove = []
        for x in clauses:
            for y in x:
                if (y[0], not y[1]) in x:
                    to_remove.append(x)
                    break
                elif (y[0] == "⊤" and y[1] is True) or (y[0] == "⊥" and y[1] is False):
                    to_remove.append(x)
                    break
        for x in to_remove:
            clauses.remove(x)

    def contra_elim(clauses: list):
        for x in clauses:
            for y in x:
                if (y[0] == "⊥" and y[1] is True) or (y[0] == "⊤" and y[1] is False):
                    x.remove(y)
                    break

    def get_unique_names(clauses: list) -> Set[str]:
        uniques = SolverClause()
        for x in clauses:
            for y in x:
                try:
                    uniques.add(SolverVariable(y[0], y[1]))
                except Exception:
                    raise RuntimeError()
        return uniques

    # Future TODO: use two watched literals algorithm to optimise backtracking
    def dpll(clauses: list, verbose: bool = False, depth: int = 0) -> SolverResult:
        # unique_var_names = Solver.get_unique_names(clauses)
        model = []
        # model += Solver.pure_literal_elim(clauses, unique_var_names, verbose=verbose)
        Solver.taut_elim(clauses)

        internal_verbose = verbose and verbosity_config.SOLVER_VERBOSE
        if internal_verbose:
            print(f"Current depth {depth}")

        (new_clauses, new_model) = Solver.propagate(clauses)
        model += new_model

        if len(new_clauses) == 0:
            ret_val = SolverResult(True, model)
            return ret_val
        elif set() in new_clauses:
            ret_val = SolverResult(False, None)
            return ret_val

        unique_var_names = Solver.get_unique_names(new_clauses)

        var = next(iter(unique_var_names))

        new_clauses_with_not_var = copy.deepcopy(new_clauses)

        not_var = SolverVariable(var[0], not var[1])
        newset = set()
        newset.add(var)
        new_clauses.append(newset)

        newset = set()
        newset.add(not_var)
        new_clauses_with_not_var.append(newset)

        (satisfiable, new_model) = Solver.dpll(new_clauses, verbose=internal_verbose, depth=depth+1)
        if (satisfiable):
            model += new_model
            return SolverResult(True, model)
        else:
            (satisfiable2, new_model_2) = Solver.dpll(new_clauses_with_not_var, verbose=internal_verbose, depth=depth+1)
            if (satisfiable2 is False):
                return SolverResult(False, None)
            else:
                model += new_model_2
                return SolverResult(True, model)

    def solve(old_clauses: Set[Tree], verbose: bool = False) -> SolverResult:
        """Returns a tuple in the form (True/False if Satisfiable/Unsat, [list of variables that form the model if sat, else None])"""
        clauses = list()
        # unique_var_names = set()
        for x in old_clauses:
            vars = Solver.transform_to_variables(x, verbose=verbose and verbosity_config.SOLVER_VERBOSE)
            clauses.append(vars)

        Solver.contra_elim(clauses)  # Didn't check for Bottom in parser/transformer, so do it now.
        return Solver.dpll(clauses, verbose=verbose and verbosity_config.SOLVER_VERBOSE)
