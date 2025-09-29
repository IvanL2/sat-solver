import copy
from dataclasses import dataclass
import logging
from dpll.logic_tree import LogicTree
from dpll.semantics import Semantics
from dpll.types import Operator, Variable


# used internally by Transformer.naming
@dataclass(frozen=True, eq=True)
class Config:
    """
    Configuration for the CNF transform algorithm.

    disable_syntax_check (bool):
        By default, the transform method performs a Parser.syntax_checkr

    use_tseytin_transform (bool):
        Applies the Tseytin transform, avoiding exponential blowup of clauses
        w.r.t the size of input tree. As this is an asymptotic assumption,
        usage may result in longer clauses for smaller input formulas.
    """
    disable_syntax_check: bool
    use_tseytin_transform: bool


default_config = Config(
    disable_syntax_check=False,
    use_tseytin_transform=True
)

_logger = logging.getLogger(f"{__name__}")


class Transformer:

    _current_fresh_num: int = 0

    _pedantic: bool = True

    @staticmethod
    def transform(tree: LogicTree, input_config: Config | None = None) -> set[LogicTree]:
        """
        Main entry point. Transforms the input (prop. logic) parse tree into
        an equisatisfiable set of clauses (where each clause is still a tree).

        Optionally accepts a Config object, which configures optional features.
        See the dataclass itself
        """
        config = input_config if input_config is not None else default_config

        if not config.disable_syntax_check:
            LogicTree.validate_tree_and_raise(tree)

        _logger.info("Begin CNF transform")

        named_clauses: list[LogicTree] = []
        Semantics.polarise(tree)
        _logger.debug("Added polarity info to input tree")

        if config.use_tseytin_transform:
            Transformer._naming(tree=tree, clauses=named_clauses)
            named_clauses.append(tree)
            _logger.debug(f"Tseytin transform applied. Resultant formulas: {"\n".join(map(str, named_clauses))}")
        else:
            _logger.debug("Tseytin transform disabled")

        clauses: set[LogicTree] = set()

        for x in named_clauses:
            Transformer._generate_clauses(x, clauses)

        _logger.debug(f"Generated {len(clauses)} clauses: {'\n'.join(map(str, clauses))}")
        _logger.info("CNF transform done")

        return clauses

    @staticmethod
    def _generate_clauses(tree: LogicTree, clauses: set[LogicTree]) -> None:
        """
        1) Replace <-> with conj. of disj. (a <-> b) => (¬a v b) /\\ (a v ¬b)
        2) Replace -> with alternative (a -> b) => (¬a v b)
        3) Push negation as far in as possible, i.e. ¬(a v b) => ¬a n ¬b
        4) Remove double negations (¬¬a => a)
        5) Transform any DNFs left into CNFs
        6) Split CNF into clauses
        """
        new_tree = Transformer._replace_equivs(tree)
        new_tree = Transformer._replace_implics(new_tree)
        new_tree = Transformer._push_negations(new_tree)
        new_tree = Transformer._double_neg_remove(new_tree)
        new_tree = Transformer._dnf_to_cnf(new_tree)
        Transformer._split_conjunctions(new_tree, clauses)

    @staticmethod
    def _replace_equivs(tree: LogicTree) -> LogicTree:
        """
        # Post-order DFS traversal, returns a transformed tree free of equivalences
        #
        # Impossible to introduce an equivalence to a child node; so safe to post-order (to avoid big deepcopy) and not pre-order
        """

        left_tree, right_tree = LogicTree.map_lr_if_not_none(
            Transformer._replace_equivs,
            tree
        )

        match tree.value:
            case Operator.EQUIVALENCE:  # Left/right guaranteed to exist by syntax check
                negated_original_left = LogicTree(Operator.NEGATION, left=copy.deepcopy(left_tree))
                negated_original_right = LogicTree(Operator.NEGATION, left=copy.deepcopy(right_tree))
                not_a_v_b = LogicTree(Operator.DISJUNCTION, left=negated_original_left, right=right_tree)
                a_v_not_b = LogicTree(Operator.DISJUNCTION, left=left_tree, right=negated_original_right)
                new_tree = LogicTree(Operator.CONJUNCTION, left=not_a_v_b, right=a_v_not_b)
                return new_tree
            case _:
                return LogicTree(tree.value, left=left_tree, right=right_tree)

    @staticmethod
    def _replace_implics(tree: LogicTree) -> LogicTree:
        """
        # Post-order DFS traversal, returns a transformed tree free of implications
        #
        # Impossible to introduce an implication to a child node; to safe to post-order (to avoid big deepcopy) and not pre-order
        """

        left_tree, right_tree = LogicTree.map_lr_if_not_none(
            Transformer._replace_implics,
            tree
        )

        match tree.value:
            case Operator.IMPLICATION:
                new_left = LogicTree(Operator.NEGATION, left=left_tree, right=copy.deepcopy(right_tree))
                new_tree = LogicTree(Operator.DISJUNCTION, left=new_left, right=right_tree)
                new_tree.value = Operator.DISJUNCTION
                return new_tree
            case _:
                return LogicTree(tree.value, left=left_tree, right=right_tree)

    @staticmethod
    def _push_negations(tree: LogicTree) -> LogicTree:
        """
        Assumes there are no <-> or ->
        Done in pre-order traversal
        """
        left_tree_value = tree.left_value_if_not_none()

        match (tree.value, left_tree_value):
            case (Operator.NEGATION, Operator.CONJUNCTION) | (Operator.NEGATION, Operator.DISJUNCTION):
                if left_tree_value is Operator.CONJUNCTION:
                    inv_op = Operator.DISJUNCTION
                else:
                    inv_op = Operator.CONJUNCTION
                assert (tree.left is not None and tree.left.left is not None and tree.left.right is not None)
                new_left = LogicTree(Operator.NEGATION, left=copy.deepcopy(tree.left.left))
                new_right = LogicTree(Operator.NEGATION, left=copy.deepcopy(tree.left.right))
                new_left = Transformer._push_negations(new_left)
                new_right = Transformer._push_negations(new_right)
                new_tree = LogicTree(inv_op, left=new_left, right=new_right)
                return new_tree
            case (Operator(), _):
                new_left, new_right = LogicTree.map_lr_if_not_none(Transformer._push_negations, tree)
                new_tree = LogicTree(tree.value, left=new_left, right=new_right)
                return new_tree

            case _:
                return tree

    @staticmethod
    def _double_neg_remove(tree: LogicTree) -> LogicTree:
        """
        """

        left_tree_value = tree.left_value_if_not_none()

        match (tree.value, left_tree_value):
            case (Operator.NEGATION, Operator.NEGATION):
                assert tree.left is not None and tree.left.left is not None
                return Transformer._double_neg_remove(tree.left.left)
            case (Operator.NEGATION, _):
                assert type(left_tree_value) is not Operator, f"{str(tree)}"
                return tree
            case (Operator(), _):
                assert tree.left is not None and tree.right is not None, f"{str(tree)} {str(type(tree.left))}"
                new_left = Transformer._double_neg_remove(tree.left)
                new_right = Transformer._double_neg_remove(tree.right)
                new_tree = LogicTree(tree.value, left=new_left, right=new_right)
                return new_tree
            case _:
                return tree

    @staticmethod
    def _dnf_to_cnf(tree: LogicTree) -> LogicTree:
        """
        temp
        """
        left_tree, right_tree = LogicTree.map_lr_if_not_none(Transformer._dnf_to_cnf, tree)
        left_tree_value = tree.left_value_if_not_none()
        right_tree_value = tree.right_value_if_not_none()

        match (tree.value, left_tree_value, right_tree_value):
            case (Operator.NEGATION, _, _):
                return tree
            case (Operator.DISJUNCTION, Operator.CONJUNCTION, Operator.CONJUNCTION):
                # (A n B) v (C n D) => [(A v C) n (A v D)] n [(B v C) n (B v D)]
                assert left_tree is not None and left_tree.left is not None and left_tree.right is not None
                assert right_tree is not None and right_tree.left is not None and right_tree.right is not None
                a_v_c = LogicTree(Operator.DISJUNCTION, left=left_tree.left, right=right_tree.left)
                a_v_d = LogicTree(Operator.DISJUNCTION, left=left_tree.left, right=right_tree.right)
                b_v_c = LogicTree(Operator.DISJUNCTION, left=left_tree.right, right=right_tree.left)
                b_v_d = LogicTree(Operator.DISJUNCTION, left=left_tree.right, right=right_tree.right)
                left = LogicTree(Operator.CONJUNCTION, left=a_v_c, right=a_v_d)
                right = LogicTree(Operator.CONJUNCTION, left=b_v_c, right=b_v_d)
                new_tree = LogicTree(Operator.CONJUNCTION, left=left, right=right)
                return Transformer._dnf_to_cnf(new_tree)
            case (Operator.DISJUNCTION, Operator.CONJUNCTION, _):
                # CNF within DNF detected
                # (A n B) v C => (A v C) n (B v C)
                assert left_tree is not None and left_tree.left is not None and left_tree.right is not None
                assert right_tree is not None
                new_left = LogicTree(Operator.DISJUNCTION, left=left_tree.left, right=copy.deepcopy(right_tree))
                new_right = LogicTree(Operator.DISJUNCTION, left=left_tree.right, right=copy.deepcopy(right_tree))
                new_tree = LogicTree(Operator.CONJUNCTION, left=new_left, right=new_right)
                return Transformer._dnf_to_cnf(new_tree)
            case (Operator.DISJUNCTION, _, Operator.CONJUNCTION):
                assert left_tree is not None
                assert right_tree is not None and right_tree.left is not None and right_tree.right is not None
                new_left = LogicTree(Operator.DISJUNCTION, left=copy.deepcopy(left_tree), right=right_tree.left)
                new_right = LogicTree(Operator.DISJUNCTION, left=copy.deepcopy(left_tree), right=right_tree.right)
                new_tree = LogicTree(Operator.CONJUNCTION, left=new_left, right=new_right)
                return Transformer._dnf_to_cnf(new_tree)
            case (Operator(), _, _):
                return LogicTree(tree.value, left_tree, right_tree)
            case _:
                return LogicTree(tree.value)

    @staticmethod
    def _split_conjunctions(tree: LogicTree, clauses: set[LogicTree]) -> None:

        match tree.value:
            case Operator.CONJUNCTION:
                assert tree.left is not None and tree.right is not None
                Transformer._split_conjunctions(tree.left, clauses)
                Transformer._split_conjunctions(tree.right, clauses)
            case _:
                clauses.add(tree)

    @staticmethod
    def _get_lr_pol_mult(tree: LogicTree) -> tuple[int, int]:
        match tree.value:
            case Operator.NEGATION:
                return (-1, 999)
            case Operator.CONJUNCTION | Operator.DISJUNCTION:
                return (1, 1)
            case Operator.IMPLICATION:
                return (-1, 1)
            case Operator.EQUIVALENCE:
                return (0, 0)
            case _:
                return (999, 999)

    @staticmethod
    def _naming(tree: LogicTree, clauses: list[LogicTree], first: bool = True, pol: int = 1) -> None:
        """
        Post-order traversal to name from bottom up
        IMPORTANT: We assume tseytin transformation has been applied already,
                   such that at most there is one embedded equivalenci
        current_fresh_num is a singleton list acting like an int by reference
        """
        global _current_fresh_num

        if first:
            _current_fresh_num = 0

        left_mult, right_mult = Transformer._get_lr_pol_mult(tree)
        left_pol = left_mult * pol
        right_pol = right_mult * pol

        if tree.left is not None:
            Transformer._naming(tree.left, clauses, first=False, pol=left_pol)
        if tree.right is not None:
            Transformer._naming(tree.right, clauses, first=False, pol=right_pol)

        match tree.value:
            case (Operator.NEGATION):
                return
            case Operator():
                newvar = Variable("n"+str(_current_fresh_num))
                if pol == 1:
                    clauses.append(LogicTree(Operator.IMPLICATION, left=LogicTree(newvar), right=copy.deepcopy(tree)))
                elif pol == 0:
                    clauses.append(LogicTree(Operator.EQUIVALENCE, left=LogicTree(newvar), right=copy.deepcopy(tree)))
                elif pol == -1:
                    clauses.append(LogicTree(Operator.IMPLICATION, left=copy.deepcopy(tree), right=LogicTree(newvar)))
                else:
                    raise RuntimeError(f"Got undefined polarity {pol}")

                # Update current node
                tree.value = newvar
                tree.left = None
                tree.right = None

                _current_fresh_num += 1
            case _:
                return
