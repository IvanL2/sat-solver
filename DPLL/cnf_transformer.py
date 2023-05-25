from tree import Tree
from parser import Parser
import copy
from semantics import *

class Transformer:
    def transform(tree : Tree):
        named_clauses = []
        Semantics.polarise(tree)
        Transformer.naming(tree=tree, clauses=named_clauses)
        named_clauses.append(tree)
        clauses = set()
        for x in named_clauses:
            Transformer.generate_clauses(x, clauses)
        return clauses
    
    def replace_equivs(tree: Tree):
        left_or_right = "left" if (tree.parent == None or tree.parent.left == tree) else "right"
        modified = False
        if isinstance(tree.value, Operator) and tree.value.name == "=":
            # (A <-> B) => (¬A v B) n (A v ¬B)
            original_left = tree.left
            original_right = tree.right
            negated_original_left = Tree(Operator.Negation(), left=copy.deepcopy(original_left))
            negated_original_right = Tree(Operator.Negation(), left=copy.deepcopy(original_right))
            not_a_v_b = Tree(Connective.Disjunction(), left=negated_original_left, right=original_right)
            a_v_not_b = Tree(Connective.Disjunction(), left=original_left, right=negated_original_right)
            final = Tree(Connective.Conjunction(), left=not_a_v_b, right=a_v_not_b)
            
            # Find parent, and replace node with new
            parent = tree.parent
            final.parent = parent
            if parent.left == tree:
                parent.left = final
            else:
                parent.right = final
        currenttree = tree
        if modified:
            currenttree = tree.parent.left if (left_or_right == "left") else tree.parent.right
        if currenttree.left != None:
            Transformer.replace_equivs(currenttree.left)
        if currenttree.right != None:
            Transformer.replace_equivs(currenttree.right)

    def replace_implics(tree: Tree):
        left_or_right = "left" if (tree.parent == None or tree.parent.left == tree) else "right"
        modified = False
        if isinstance(tree.value, Operator) and tree.value.name == ">":
            # (A -> B) => (¬A v B)
            newleft = Tree(Operator.Negation(), left=tree.left)
            final = Tree(Connective.Disjunction(), left=newleft, right=tree.right)
            # Find parent, and replace node with new
            parent = tree.parent
            final.parent = parent
            if parent.left == tree:
                parent.left = final
            else:
                parent.right = final
        currenttree = tree
        if modified:
            currenttree = tree.parent.left if (left_or_right == "left") else tree.parent.right
        if currenttree.left != None:
            Transformer.replace_implics(currenttree.left)
        if currenttree.right != None:
            Transformer.replace_implics(currenttree.right)

    def push_negations(tree: Tree):
        """
        Assumes there are no <-> or ->
        Done in pre-order traversal
        """
        parent = tree.parent
        left_or_right = "left" if (parent == None or parent.left == tree) else "right"
        modified = False
        if isinstance(tree.value, Operator) and tree.value.name == "!" and isinstance(tree.left.value, Connective):
            newleft = Tree(Operator.Negation(), left=copy.deepcopy(tree.left.left))
            newright = Tree(Operator.Negation(), left=copy.deepcopy(tree.left.right))
            if tree.left.value.name == "&":
                # ¬(A n B) => (¬A v ¬B)
                if parent.left == tree:
                    parent.left = Tree(Connective.Disjunction(), parent=parent, left=newleft, right=newright)
                else:
                    parent.right = Tree(Connective.Disjunction(), parent=parent, left=newleft, right=newright)
            elif tree.left.value.name == "|":
                 # ¬(A v B) => (¬A n ¬B)     
                if parent.left == tree:
                    parent.left = Tree(Connective.Conjunction(), parent=parent, left=newleft, right=newright)
                else:
                    parent.right = Tree(Connective.Conjunction(), parent=parent, left=newleft, right=newright)
            modified = True
        currenttree = tree
        if modified:
            currenttree = parent.left if (left_or_right == "left") else parent.right
        if currenttree.left != None:
                Transformer.push_negations(currenttree.left)
        if currenttree.right != None:
            Transformer.push_negations(currenttree.right)
            
    
    def double_neg_remove(tree: Tree):
        modified = False
        left_or_right = "left" if (tree.parent == None or tree.parent.left == tree) else "right"
        if isinstance(tree.value, Operator) and tree.value.name == "!":
            if tree.left.value.name == "!":
                # Double negation detected
                parent = tree.parent
                if parent.left == tree:
                    parent.left = copy.deepcopy(tree.left.left)
                else:
                    parent.right = copy.deepcopy(tree.left.left)
            modified = True
        currenttree = tree
        if modified:
            currenttree = tree.parent.left if (left_or_right == "left") else tree.parent.right
        if currenttree.left != None:
            Transformer.double_neg_remove(currenttree.left)
        if currenttree.right != None:
            Transformer.double_neg_remove(currenttree.right)
    
    def dnf_to_cnf(tree: Tree):
        modified = False
        # This is really ugly, but it works
        parent_tree_direction_to_current_tree = "left" if tree.parent != None and tree.parent.left == tree else "right"
        if isinstance(tree.value, Operator) and tree.value.name == "|":
            if isinstance(tree.right.value, Operator) and (tree.left.value.name == "&") and isinstance(tree.right.value, Operator) and tree.right.value.name == "&":
                #(A n B) v (C n D) => [(A v C) n (A v D)] n [(B v C) n (B v D)]
                a_v_c = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right.left))
                a_v_d = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right.right))
                b_v_c = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right.left))
                b_v_d = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right.right))
                left = Tree(Connective.Conjunction(), left=a_v_c, right=a_v_d)
                right = Tree(Connective.Conjunction(), left=b_v_c, right=b_v_d)
                final = Tree(Connective.Conjunction(), left=left, right=right)
                final.parent = tree.parent
                if tree.parent.left == tree:
                    tree.parent.left = final
                else:
                    tree.parent.right = final
                modified = True
            elif isinstance(tree.left.value, Operator) and tree.left.value.name == "&":
                # CNF within DNF detected
                # (A n B) v C => (A v C) n (B v C)
                a_v_c = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left.left), right=copy.deepcopy(tree.right))
                b_v_c = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left.right), right=copy.deepcopy(tree.right))
                final = Tree(Connective.Conjunction(), left=a_v_c, right=b_v_c)
                final.parent = tree.parent
                if tree.parent.left == tree:
                    tree.parent.left = final
                else:
                    tree.parent.right = final
                modified = True
            elif isinstance(tree.right.value, Operator) and tree.right.value.name == "&":
                # CNF within DNF detected
                # A v (B n C) => (A v B) n (A v C)
                a_v_b = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left), right=copy.deepcopy(tree.right.left))
                a_v_c = Tree(Connective.Disjunction(), left=copy.deepcopy(tree.left), right=copy.deepcopy(tree.right.right))
                final = Tree(Connective.Conjunction(), left=a_v_c, right=a_v_b)
                final.parent = tree.parent
                if tree.parent.left == tree:
                    tree.parent.left = final
                else:
                    tree.parent.right = final
                modified = True
        newtree = tree if tree.parent == None else tree.parent.left if (parent_tree_direction_to_current_tree == "left") else tree.parent.right
        if newtree.left != None:
            # If any child tree was changed, then need to check entire tree again
            if Transformer.dnf_to_cnf(newtree.left): Transformer.dnf_to_cnf(newtree)
        if newtree.right != None:
            if Transformer.dnf_to_cnf(newtree.right): Transformer.dnf_to_cnf(newtree)
        # At this point, all child nodes should've been checked, and up to this point
        # everything is in CNF, but might fail at parent if anything changed, hence return modified.
        return modified
    
    def split_conjunctions(tree: Tree, clauses: set):
        if tree.value == "start":
            Transformer.split_conjunctions(tree.left, clauses)
            return
        if isinstance(tree.value, Operator) and tree.value.name == "&":
            Transformer.split_conjunctions(tree.left, clauses)
            Transformer.split_conjunctions(tree.right, clauses)
        else:
            clauses.add(tree)

    def generate_clauses(tree : Tree, clauses: set) -> set:
        """
        1) Replace <-> with conj. of disj. (a <-> b) => (¬a v b) /\ (a v ¬b) 
        2) Replace -> with alternative (a -> b) => (¬a v b)
        3) Push negation as far in as possible, i.e. ¬(a v b) => ¬a n ¬b
        4) Remove double negations (¬¬a => a)
        5) Transform any DNFs left into CNFs
        6) Split CNF into clauses
        """
        Transformer.replace_equivs(tree)
        Transformer.replace_implics(tree)
        Transformer.push_negations(tree)
        Transformer.double_neg_remove(tree)
        Transformer.dnf_to_cnf(tree)
        Transformer.split_conjunctions(tree, clauses)

    # Post-order traversal to name from bottom up
    def naming(tree: Tree, clauses: list):
        if tree.left != None:
            Transformer.naming(tree.left, clauses)
        if tree.right != None:
            Transformer.naming(tree.right, clauses)

        if isinstance(tree.value, Operator):
            newvar = Variable("n"+str(len(clauses)))
            if tree.pol == 1:
                clauses.append(Tree("start",left=Tree(
                            Connective.Implication(),
                            left=Tree(newvar),right=copy.deepcopy(tree))))
            elif tree.pol == 0:
                clauses.append(Tree("start",left=Tree(
                            Connective.Equivalence(),
                            left=Tree(newvar),right=copy.deepcopy(tree))))
            elif tree.pol == -1:
                clauses.append(Tree("start",left=Tree(
                            Connective.Implication(),
                            left=copy.deepcopy(tree),right=Tree(newvar))))
            else:
                print("ERROR")
                raise RuntimeError()
            parent = tree.parent
            if parent.left == tree:
                parent.left = Tree(newvar)
                parent.left.parent = parent
            else:
                parent.right = Tree(newvar)
                parent.right.parent = parent