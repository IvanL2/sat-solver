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

    taut_true_lit = SolverVariable("⊤", True)
    taut_false_lit = SolverVariable("⊤", False)
    contra_true_lit = SolverVariable("⊥", True)
    contra_false_lit = SolverVariable("⊥", False)

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

        unit_clauses = [clause for clause in clauses if len(clause) == 1]
        model = []

        while unit_clauses:
            literal = next(iter(unit_clauses[0]))
            model.append(literal)

            new_clauses = [clause for clause in new_clauses if literal not in clause]
            negated_literal = SolverVariable(literal.name, not literal.polarity)

            for c in new_clauses:
                if negated_literal in c:
                    c.remove(negated_literal)

            unit_clauses = unit_clauses = [clause for clause in new_clauses if len(clause) == 1]

        clauses[:] = new_clauses
        return model

    def pure_literal_elim(clauses: List[SolverClause]) -> List[SolverVariable]:
        var_occurrences = {}

        # "Count" occurrences of positive and negative literals; store as bool because we only
        # care "count > 0" in the context of pure lits
        for clause in clauses:
            for var in clause:
                if var.name not in var_occurrences:
                    var_occurrences[var.name] = {True: False, False: False}
                var_occurrences[var.name][var.polarity] = True

        pure_literals = []

        # Needs profiling; may store original variable to avoid reconstructing
        for var_name, counts in var_occurrences.items():
            if counts[True] and not counts[False]:
                pure_literals.append(SolverVariable(var_name, False))
            elif counts[False] and not counts[True]:
                pure_literals.append(SolverVariable(var_name, True))

        # Remove clauses containing pure literals and simplify remaining clauses
        new_clauses = []
        for clause in clauses:
            if not any(pure in clause for pure in pure_literals):  # If not pure lit
                new_clauses.append(clause)

        clauses[:] = new_clauses  # Modify the original clauses list in-place
        return pure_literals

    def taut_elim(clauses: list) -> List[SolverVariable]:
        new_clauses = []
        for clause in clauses:
            if not(Solver.taut_true_lit in clause or Solver.contra_false_lit in clause):
                new_clauses.append(clause)
        clauses[:] = new_clauses

    def contra_elim(clauses: list):
        for clause in clauses:
            if Solver.contra_true_lit in clause:
                clause.remove(Solver.contra_true_lit)
            if Solver.taut_false_lit in clause:
                clause.remove(Solver.taut_false_lit)

    def get_unique_names(clauses: list) -> Set[str]:
        uniques = SolverClause()
        for x in clauses:
            for y in x:
                uniques.add(y)
        return uniques

    # Future TODO: use two watched literals algorithm to optimise backtracking
    def dpll(clauses: list, enable_pure_lit_elim: bool = False, verbose: bool = False, depth: int = 0) -> SolverResult:
        model = []
        new_clauses = copy.deepcopy(clauses)

        if (enable_pure_lit_elim):
            model += Solver.pure_literal_elim(new_clauses)
        Solver.taut_elim(new_clauses)

        internal_verbose = verbose and verbosity_config.SOLVER_VERBOSE
        if internal_verbose:
            print(f"Current depth {depth}")

        model += Solver.propagate(new_clauses)

        if len(new_clauses) == 0:
            ret_val = SolverResult(True, model)
            return ret_val
        elif set() in new_clauses:
            ret_val = SolverResult(False, None)
            return ret_val

        var = next(iter(new_clauses[0]))

        new_clauses_with_not_var = copy.deepcopy(new_clauses)

        not_var = SolverVariable(var.name, not var.polarity)
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
