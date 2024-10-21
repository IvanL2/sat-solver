from typing import List, Set
from .tree import Tree
from .pl_parser import Parser
from .semantics import *
import copy
from . import verbosity_config

class Transformer:
    def transform(tree : Tree, verbose: bool=False) -> Set[Tree]:
        steps_verbose = verbose and verbosity_config.TRANSFORMER_STEPS_VERBOSE
        named_clauses = []
        Semantics.polarise(tree)
        names = set()
        Transformer.get_names(tree, names)
        if steps_verbose: print("Added polarity information to tree.")
        Transformer.naming(tree=tree, clauses=named_clauses, set_of_names=names, current_fresh_num=[0])
        named_clauses.append(tree)
        if steps_verbose:
            print(f"Applied naming algorithm (Tseytin transformation).\nResulting clauses:")
            for x in named_clauses:
                Parser.print_exp(x)
        clauses = set()
        for x in named_clauses:
            Transformer.generate_clauses(x, clauses, verbose=steps_verbose)
        if verbose and verbosity_config.TRANSFORMER_RESULT_VERBOSE:
            print(f"Transformed into CNF:")
            for x in clauses:
                Parser.print_exp(x)
        return clauses

    def replace_equivs(tree: Tree, parent: Tree=None):
        """
        # Post-order DFS traversal, returns a transformed tree free of equivalences
        # 
        # Impossible to introduce an equivalence to a child node; to safe to post-order (to avoid big deepcopy) and not pre-order
        """

        if tree == None or isinstance(tree.value, Variable):
            return tree

        new_tree = Tree(None, parent=parent)
        left_tree = Transformer.replace_equivs(tree.left, new_tree)
        right_tree = Transformer.replace_equivs(tree.left, new_tree)

        if isinstance(tree.value, Operator) and tree.value == Operator.EQUIVALENCE:
            # (A <-> B) => (¬A v B) n (A v ¬B)
            negated_original_left = Tree(Operator.NEGATION, left=copy.deepcopy(left_tree))
            negated_original_right = Tree(Operator.NEGATION, left=copy.deepcopy(right_tree))
            not_a_v_b = Tree(Operator.DISJUNCTION, left=negated_original_left, right=right_tree)
            a_v_not_b = Tree(Operator.DISJUNCTION, left=left_tree, right=negated_original_right)
            new_tree.value = Operator.CONJUNCTION
            new_tree.left = not_a_v_b
            new_tree.right = a_v_not_b
        else:
            return tree

        return new_tree

    
    def replace_implics(tree: Tree, parent: Tree=None):
        """
        # Post-order DFS traversal, returns a transformed tree free of implications
        # 
        # Impossible to introduce an implication to a child node; to safe to post-order (to avoid big deepcopy) and not pre-order
        """
        
        if tree == None or isinstance(tree.value, Variable):
            return tree

        new_tree = Tree(None, parent=parent)
        left_tree = Transformer.replace_implics(tree.left, new_tree)
        right_tree = Transformer.replace_implics(tree.right, new_tree)

        if isinstance(tree.value, Operator) and tree.value == Operator.IMPLICATION:
            # (A -> B) => (¬A v B)
            new_left = Tree(Operator.NEGATION, parent=new_tree, left=left_tree)
            new_tree.value = Operator.DISJUNCTION
            new_tree.left = new_left
            new_tree.right = right_tree
        else:
            return tree

        return new_tree

    def push_negations(tree: Tree, parent: Tree=None):
        """
        Assumes there are no <-> or ->
        Done in pre-order traversal
        """
        if tree == None or isinstance(tree.value, Variable):
            return tree
        
        new_tree = Tree(None, parent=parent)

        if tree.value == Operator.NEGATION and isinstance(tree.left.value, Operator):

            if tree.left.value == Operator.CONJUNCTION:
                new_left = Tree(Operator.NEGATION, parent=new_tree, left=copy.deepcopy(tree.left.left))
                new_left = Transformer.push_negations(new_left)
                new_right = Tree(Operator.NEGATION, parent=new_tree, left=copy.deepcopy(tree.left.right))
                new_right = Transformer.push_negations(new_right)
                new_tree.left = new_left
                new_tree.right = new_right
                new_tree.value = Operator.DISJUNCTION
            
            elif tree.left.value == Operator.DISJUNCTION:
                new_left = Tree(Operator.NEGATION, parent=new_tree, left=copy.deepcopy(tree.left.left))
                new_left = Transformer.push_negations(new_left)
                new_right = Tree(Operator.NEGATION, parent=new_tree, left=copy.deepcopy(tree.left.right))
                new_right = Transformer.push_negations(new_right)
                new_tree.left = new_left
                new_tree.right = new_right
                new_tree.value = Operator.CONJUNCTION

        if (new_tree.value == None):
            new_tree.value = tree.value
            new_tree.left = Transformer.push_negations(tree.left)
            new_tree.right = Transformer.push_negations(tree.right)
        
        return new_tree

    def double_neg_remove(tree: Tree, parent: Tree=None):
        """
        """
        if tree == None or isinstance(tree.value, Variable):
            return tree

        new_tree = Tree(tree.value, parent=parent)

        if tree.value == Operator.NEGATION and tree.left.value == Operator.NEGATION:
            return Transformer.double_neg_remove(tree.left.left, parent=new_tree)
        else:
            new_tree = Tree(tree.value, parent=parent)
            new_tree.left = Transformer.double_neg_remove(tree.left, parent=new_tree)
            new_tree.right = Transformer.double_neg_remove(tree.right, parent=new_tree)
            return new_tree
    
    def dnf_to_cnf(tree: Tree, parent: Tree=None):
        """
        
        """
        if tree == None or isinstance(tree.value, Variable):
            return tree
        
        if tree.value == Operator.NEGATION: # By this time, negations only on literals
            return tree

        new_tree = Tree(tree.value)
        new_tree.left = tree.left # default to old left/right
        new_tree.right = tree.right

        if tree.value == Operator.DISJUNCTION:
            if isinstance(tree.left.value, Operator) and (tree.left.value == Operator.CONJUNCTION) and isinstance(tree.right.value, Operator) and (tree.right.value == Operator.CONJUNCTION):
                #(A n B) v (C n D) => [(A v C) n (A v D)] n [(B v C) n (B v D)]
                new_tree.value = Operator.CONJUNCTION
                left  = Tree(Operator.CONJUNCTION, parent=new_tree, left=None, right=None)
                right = Tree(Operator.CONJUNCTION, parent=new_tree, left=None, right=None)
                a_v_c = Tree(Operator.DISJUNCTION, parent=left, left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right.left))
                a_v_d = Tree(Operator.DISJUNCTION, parent=left, left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right.right))
                b_v_c = Tree(Operator.DISJUNCTION, parent=right, left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right.left))
                b_v_d = Tree(Operator.DISJUNCTION, parent=right, left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right.right))
                left.left = a_v_c
                left.right = a_v_d
                right.left = b_v_c
                right.right = b_v_d
            elif isinstance(tree.left.value, Operator) and tree.left.value == Operator.CONJUNCTION:
                # CNF within DNF detected
                # (A n B) v C => (A v C) n (B v C)
                new_tree.value = Operator.CONJUNCTION
                new_tree.left = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right))
                new_tree.right = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right))
            elif isinstance(tree.right.value, Operator) and tree.right.value == Operator.CONJUNCTION:
                # CNF within DNF detected
                # A v (B n C) => (A v B) n (A v C)
                new_tree.value = Operator.CONJUNCTION
                new_tree.left = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left), right=copy.deepcopy(tree.right.left))
                new_tree.right = Tree(Operator.DISJUNCTION, left=copy.deepcopy(tree.left), right=copy.deepcopy(tree.right.right))

        new_tree.left = Transformer.dnf_to_cnf(new_tree.left)
        new_tree.right = Transformer.dnf_to_cnf(new_tree.right)

        return new_tree

    
    def split_conjunctions(tree: Tree, clauses: Set[Tree]):
        if isinstance(tree.value, Operator) and tree.value == Operator.CONJUNCTION:
            Transformer.split_conjunctions(tree.left, clauses)
            Transformer.split_conjunctions(tree.right, clauses)
        else:
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
        if tree.left != None:
            Transformer.get_names(tree.left, names)
        if tree.right != None:
            Transformer.get_names(tree.right, names)
        if tree.left == None and tree.right == None:
            names.add(tree.value.name)
    
    # Post-order traversal to name from bottom up
    # IMPORTANT: We assume tseytin transformation has been applied already,
    #            such that at most there is one embedded equivalence
    def naming(tree: Tree, clauses: list, set_of_names: set, current_fresh_num: List[int]=[0]) -> int:
        if tree == None or isinstance(tree, Variable):
            return

        Transformer.naming(tree.left, clauses, set_of_names, current_fresh_num)
        Transformer.naming(tree.right, clauses, set_of_names, current_fresh_num)

        if isinstance(tree.value, Operator) and tree.value != Operator.NEGATION:
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