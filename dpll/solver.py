import copy
import logging
from typing import NamedTuple, Final

from dpll.types import Operator
from dpll.logic_tree import LogicTree


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
    model: list[SolverVariable]


SolverClause = set[SolverVariable]


class Solver:
    """Implements (a naive version) of the DPLL algorithm"""

    _logger = logging.getLogger(f"{__name__}")
    taut_true_lit: Final = SolverVariable("⊤", True)
    taut_false_lit: Final = SolverVariable("⊤", False)
    contra_true_lit: Final = SolverVariable("⊥", True)
    contra_false_lit: Final = SolverVariable("⊥", False)

    @staticmethod
    def _get_literals(tree: LogicTree) -> list[LogicTree]:
        literals: list[LogicTree] = []
        if tree.literal:
            literals.append(tree)
            return literals
        if tree.left is not None:
            literals += (Solver._get_literals(tree.left))
        if tree.right is not None:
            literals += (Solver._get_literals(tree.right))
        return literals

    @staticmethod
    def _transform_to_variables(tree: LogicTree) -> set[SolverVariable]:
        """Takes abstract syntax tree from previous steps; now in CNF so just split into tuples"""
        tree_literals = Solver._get_literals(tree)  # Collect

        Solver._logger.debug(f"Literals of {str(tree)}: {str(tree_literals)}")

        vars = SolverClause()
        for x in tree_literals:
            if x.value is Operator.NEGATION:  # At this point, only operator is negation
                assert x.left is not None
                vars.add(SolverVariable(x.left.value.name, False))
            elif type(x.value) is not Operator:
                vars.add(SolverVariable(x.value.name, True))
            else:
                assert False, "Found non-literal operator in set of literals"
        return vars

    @staticmethod
    def propagate(clauses: list[SolverClause]) -> list[SolverVariable]:
        """DPLL unit propagation """
        new_clauses = copy.deepcopy(clauses)

        unit_clauses: list[SolverClause] = [clause for clause in clauses if len(clause) == 1]
        model: list[SolverVariable] = []

        while unit_clauses:
            literal = next(iter(unit_clauses[0]))
            model.append(literal)

            new_clauses = [clause for clause in new_clauses if literal not in clause]
            negated_literal = SolverVariable(literal.name, not literal.polarity)

            for c in new_clauses:
                if negated_literal in c:
                    Solver._logger.debug(f"Removing literal {negated_literal} from clause {c}")
                    c.remove(negated_literal)

            unit_clauses = unit_clauses = [clause for clause in new_clauses if len(clause) == 1]

        clauses[:] = new_clauses
        return model

    @staticmethod
    def pure_literal_elim(clauses: list[SolverClause]) -> list[SolverVariable]:
        var_occurrences: dict[str, dict[bool, bool]] = {}

        # "Count" occurrences of positive and negative literals; store as bool because we only
        # care "count > 0" in the context of pure lits
        for clause in clauses:
            for var in clause:
                if var.name not in var_occurrences:
                    var_occurrences[var.name] = {True: False, False: False}
                var_occurrences[var.name][var.polarity] = True

        pure_literals: list[SolverVariable] = []

        # Needs profiling; may store original variable to avoid reconstructing
        for var_name, counts in var_occurrences.items():
            if counts[True] and not counts[False]:
                pure_literals.append(SolverVariable(var_name, False))
            elif counts[False] and not counts[True]:
                pure_literals.append(SolverVariable(var_name, True))

        # Remove clauses containing pure literals and simplify remaining clauses
        new_clauses: list[SolverClause] = []
        for clause in clauses:
            if not any(pure in clause for pure in pure_literals):  # If not pure lit
                new_clauses.append(clause)

        clauses[:] = new_clauses  # Modify the original clauses list in-place
        return pure_literals

    @staticmethod
    def taut_elim(clauses: list[SolverClause]):
        new_clauses: list[SolverClause] = []
        for clause in clauses:
            if not (Solver.taut_true_lit in clause or Solver.contra_false_lit in clause):
                new_clauses.append(clause)
        clauses[:] = new_clauses

    @staticmethod
    def contra_elim(clauses: list[SolverClause]):
        for clause in clauses:
            if Solver.contra_true_lit in clause:
                clause.remove(Solver.contra_true_lit)
            if Solver.taut_false_lit in clause:
                clause.remove(Solver.taut_false_lit)

    # @staticmethod
    # def get_unique_names(clauses: list[SolverClause]) -> set[str]:
    #     uniques = SolverClause()
    #     for x in clauses:
    #         for y in x:
    #             uniques.add(y)
    #     return uniques

    # Future TODO: use two watched literals algorithm to optimise backtracking
    @staticmethod
    def dpll(clauses: list[SolverClause], enable_pure_lit_elim: bool = False, depth: int = 0) -> SolverResult:
        model: list[SolverVariable] = []
        new_clauses = copy.deepcopy(clauses)

        if (enable_pure_lit_elim):
            model += Solver.pure_literal_elim(new_clauses)
        Solver.taut_elim(new_clauses)

        Solver._logger.debug(f"Current depth {depth}, clauses: {clauses}")

        model += Solver.propagate(new_clauses)

        if len(new_clauses) == 0:
            ret_val = SolverResult(True, model)
            return ret_val
        elif set() in new_clauses:
            ret_val = SolverResult(False, [])
            return ret_val

        var = next(iter(new_clauses[0]))

        new_clauses_with_not_var = copy.deepcopy(new_clauses)

        not_var = SolverVariable(var.name, not var.polarity)
        newset: SolverClause = SolverClause()
        newset.add(var)
        new_clauses.append(newset)

        newset = set()
        newset.add(not_var)
        new_clauses_with_not_var.append(newset)

        (satisfiable, new_model) = Solver.dpll(new_clauses, depth=depth+1)
        if (satisfiable):
            model += new_model
            return SolverResult(True, model)
        else:
            (satisfiable2, new_model_2) = Solver.dpll(new_clauses_with_not_var, depth=depth+1)
            if (satisfiable2 is False):
                return SolverResult(False, [])
            else:
                model += new_model_2
                return SolverResult(True, model)

    @staticmethod
    def solve(old_clauses: set[LogicTree]) -> SolverResult:
        """Returns a tuple in the form (True/False if Satisfiable/Unsat, [list of variables that form the model if sat, else None])"""
        clauses: list[SolverClause] = list()
        # unique_var_names = set()
        for x in old_clauses:
            vars: set[SolverVariable] = Solver._transform_to_variables(x)
            clauses.append(vars)

        Solver.contra_elim(clauses)  # Didn't check for Bottom in parser/transformer, so do it now.
        return Solver.dpll(clauses)
