import copy
from typing import List, Set

from dpll.tree import Tree
from dpll.parser import Parser
from dpll.semantics import *
import dpll.verbosity_config as verbosity_config


class Transformer:
    
    def transform(tree : Tree, verbose: bool=False) -> Set[Tree]:
        internal_verbose = verbose and verbosity_config.TRANSFORMER_SUMMARY_VERBOSE
        named_clauses = []
        Semantics.polarise(tree)
        names = set()
        Transformer.get_names(tree, names)

        if internal_verbose:
            print("Added polarity information to tree.")

        Transformer.naming(tree=tree, clauses=named_clauses, set_of_names=names, current_fresh_num=[0])

        named_clauses.append(tree)

        if internal_verbose:
            print(f"Applied naming algorithm (Tseytin transformation).\nResulting clauses:")
            for x in named_clauses:
                Parser.print_exp(x)

        clauses = set()

        for x in named_clauses:
            Transformer.generate_clauses(x, clauses, verbose=verbose and verbosity_config.TRANSFORMER_STEPS_VERBOSE)

        if internal_verbose:
            print(f"Number of clauses: {len(clauses)}")
            print(f"Transformed into CNF:")
            for x in clauses:
                Parser.print_exp(x)
        return clauses

    def replace_equivs(tree: Tree):
        """
        # Post-order DFS traversal, returns a transformed tree free of equivalences
        # 
        # Impossible to introduce an equivalence to a child node; so safe to post-order (to avoid big deepcopy) and not pre-order
        """

        if tree is None:
            return tree
        
        match tree.value:
            case Operator.EQUIVALENCE:
                left_tree = Transformer.replace_equivs(tree.left)
                right_tree = Transformer.replace_equivs(tree.left)
                negated_original_left = Tree(Operator.NEGATION, left=copy.deepcopy(left_tree))
                negated_original_right = Tree(Operator.NEGATION, left=copy.deepcopy(right_tree))
                not_a_v_b = Tree(Operator.DISJUNCTION, left=negated_original_left, right=right_tree)
                a_v_not_b = Tree(Operator.DISJUNCTION, left=left_tree, right=negated_original_right)
                new_tree = Tree(Operator.CONJUNCTION, left=not_a_v_b, right=a_v_not_b)
                new_tree.value = Operator.CONJUNCTION
                new_tree.left = not_a_v_b
                new_tree.right = a_v_not_b
                return new_tree
            case _:
                return tree

    
    def replace_implics(tree: Tree):
        """
        # Post-order DFS traversal, returns a transformed tree free of implications
        # 
        # Impossible to introduce an implication to a child node; to safe to post-order (to avoid big deepcopy) and not pre-order
        """
        
        if tree is None:
            return tree
        
        match tree.value:
            case Operator.IMPLICATION:
                left_tree = Transformer.replace_implics(tree.left)
                right_tree = Transformer.replace_implics(tree.right)
                new_left = Tree(Operator.NEGATION, left=left_tree, right=right_tree)
                new_tree = Tree(Operator.DISJUNCTION, left=new_left, right=right_tree)
                new_tree.value = Operator.DISJUNCTION
                return new_tree
            case _:
                return tree

    def push_negations(tree: Tree):
        """
        Assumes there are no <-> or ->
        Done in pre-order traversal
        """
        if tree is None:
            return tree
        
        left_tree_value = None if (tree.left is None) else tree.left.value

        match (tree.value, left_tree_value):
            case (Operator.NEGATION, Operator.CONJUNCTION):
                new_left = Tree(Operator.NEGATION, left=copy.deepcopy(tree.left.left))
                new_left = Transformer.push_negations(new_left)
                new_right = Tree(Operator.NEGATION, left=copy.deepcopy(tree.left.right))
                new_right = Transformer.push_negations(new_right)
                new_tree = Tree(Operator.DISJUNCTION, left=new_left, right=new_right)
                return new_tree

            case (Operator.NEGATION, Operator.DISJUNCTION):
                new_left = Tree(Operator.NEGATION, left=copy.deepcopy(tree.left.left))
                new_left = Transformer.push_negations(new_left)
                new_right = Tree(Operator.NEGATION, left=copy.deepcopy(tree.left.right))
                new_right = Transformer.push_negations(new_right)
                new_tree = Tree(Operator.CONJUNCTION, left=new_left, right=new_right)
                return new_tree

            case (Operator(), _):
                new_left = Transformer.push_negations(tree.left)
                new_right = Transformer.push_negations(tree.right)
                new_tree = Tree(tree.value, left=new_left, right=new_right)
                return new_tree
        
            case _:
                return tree

    def double_neg_remove(tree: Tree):
        """
        """
        if tree is None:
            return tree
        
        left_tree_value = None if (tree.left is None) else tree.left.value

        match (tree.value, left_tree_value):
            case (Operator.NEGATION, Operator.NEGATION):
                return Transformer.double_neg_remove(tree.left.left)
            case (Operator(), _):
                new_left = Transformer.double_neg_remove(tree.left)
                new_right = Transformer.double_neg_remove(tree.right)
                new_tree = Tree(tree.value, left=new_left, right=new_right)
                return new_tree
            case _:
                return tree
    
    def dnf_to_cnf(tree: Tree):
        """
        
        """
        if tree is None:
            return tree

        left_tree_value = None if (tree.left is None) else tree.left.value
        right_tree_value = None if (tree.right is None) else tree.right.value

        match (tree.value, left_tree_value, right_tree_value):
            case (Operator.NEGATION, _, _):
                return tree
            case (Operator.DISJUNCTION, Operator.CONJUNCTION, Operator.CONJUNCTION):
                #(A n B) v (C n D) => [(A v C) n (A v D)] n [(B v C) n (B v D)]
                right = Tree(Operator.CONJUNCTION,  left=None, right=None)
                a_v_c = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right.left))
                a_v_d = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right.right))
                b_v_c = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right.left))
                b_v_d = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right.right))
                left = Tree(Operator.CONJUNCTION, left=a_v_c, right=a_v_d)
                right = Tree(Operator.CONJUNCTION, left=b_v_c, right=b_v_d)
                new_tree = Tree(Operator.CONJUNCTION, left=left, right=right)
                return new_tree
            case (Operator.DISJUNCTION, Operator.CONJUNCTION, _):
                # CNF within DNF detected
                # (A n B) v C => (A v C) n (B v C)
                new_left = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right))
                new_right = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right))
                new_tree = Tree(Operator.CONJUNCTION, left=new_left, right=new_right)
                return new_tree
            case (Operator.DISJUNCTION, _, Operator.CONJUNCTION):
                new_left = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left), right=copy.deepcopy(tree.right.left))
                new_right = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left), right=copy.deepcopy(tree.right.right))
                new_tree = Tree(Operator.CONJUNCTION, left=new_left, right=new_right)
                return new_tree
            case (Operator(), _, _):
                new_left = Transformer.dnf_to_cnf(tree.left)
                new_right = Transformer.dnf_to_cnf(tree.right)
                new_tree = Tree(tree.value, left=new_left, right=new_right)
                return new_tree
            case _:
                return tree
    
    def split_conjunctions(tree: Tree, clauses: Set[Tree]):

        match tree.value:
            case Operator.CONJUNCTION:
                Transformer.split_conjunctions(tree.left, clauses)
                Transformer.split_conjunctions(tree.right, clauses)
            case _:
                clauses.add(tree)

    def generate_clauses(tree : Tree, clauses: Set[Tree], verbose: bool=False):
        """
        1) Replace <-> with conj. of disj. (a <-> b) => (¬a v b) /\\ (a v ¬b) 
        2) Replace -> with alternative (a -> b) => (¬a v b)
        3) Push negation as far in as possible, i.e. ¬(a v b) => ¬a n ¬b
        4) Remove double negations (¬¬a => a)
        5) Transform any DNFs left into CNFs
        6) Split CNF into clauses
        """
        if verbose:
            print()
            print("Start transforming:", end=" ")
            Parser.print_exp(tree)
        new_tree = Transformer.replace_equivs(tree)
        if verbose:
            print(f"After equivalence replacements:", end=" ")
            Parser.print_exp(new_tree)
        new_tree = Transformer.replace_implics(new_tree)
        if verbose:
            print(f"After implication replacements:", end=" ")
            Parser.print_exp(new_tree)
        new_tree = Transformer.push_negations(new_tree)
        if verbose:
            print(f"After pushing negations:", end=" ")
            Parser.print_exp(new_tree)
        new_tree = Transformer.double_neg_remove(new_tree)
        if verbose:
            print(f"After removing double negations:", end=" ")
            Parser.print_exp(new_tree)
        new_tree = Transformer.dnf_to_cnf(new_tree)
        if verbose:
            print(f"After DNF to CNF (FINAL):", end=" ")
            Parser.print_exp(new_tree)
        Transformer.split_conjunctions(new_tree, clauses)

    def get_names(tree: Tree, names: set):
        if tree.left is not None:
            Transformer.get_names(tree.left, names)
        if tree.right is not None:
            Transformer.get_names(tree.right, names)
        if tree.left is None and tree.right is None:
            names.add(tree.value.name)
    
    # Post-order traversal to name from bottom up
    # IMPORTANT: We assume tseytin transformation has been applied already,
    #            such that at most there is one embedded equivalence
    def naming(tree: Tree, clauses: list, set_of_names: set, current_fresh_num: List[int]=[0]) -> int:
        if tree is None:
            return

        Transformer.naming(tree.left, clauses, set_of_names, current_fresh_num)
        Transformer.naming(tree.right, clauses, set_of_names, current_fresh_num)

        match tree.value:
            case (Operator.NEGATION):
                return
            case Operator():
                # Hacky way to generate fresh variable
                newvar = Variable("n"+str(current_fresh_num[0]))
                if tree.pol == 1:
                    clauses.append(Tree(Operator.IMPLICATION,left=Tree(newvar),right=copy.deepcopy(tree)))
                elif tree.pol == 0:
                    clauses.append(Tree(Operator.EQUIVALENCE,left=Tree(newvar),right=copy.deepcopy(tree)))
                elif tree.pol == -1:
                    clauses.append(Tree(Operator.IMPLICATION,left=copy.deepcopy(tree),right=Tree(newvar)))
                else:
                    print("ERROR")
                    raise RuntimeError()

                # Update current node
                tree.value = newvar
                tree.left = None
                tree.right = None

                current_fresh_num[0] += 1
            case _:
                return