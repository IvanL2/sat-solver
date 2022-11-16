from tree import Tree
from parser import Variable
from operators import *
from constants import Constant

class Transformer:
    def __init__(self):
        pass
    
    def transform(self, tree : Tree):
        names = self.naming(tree)
        clauses = set()
        for x in names:
            self.to_cnf(x)
            clauses = clauses.union(self.generate_clauses(x))
        return clauses
        
    def generate_clauses(self, tree : Tree) -> set:
        temp = set()
        if isinstance(tree, Tree):
            if isinstance(tree.get_root(), Conjunction):
                temp = temp.union(self.generate_clauses(tree.get_left()))
                temp = temp.union(self.generate_clauses(tree.get_right()))
                return temp
        temp.add(tree)
        return temp

    def to_cnf(self, tree : Tree):
        while True:
            if not self._is_operator_in_tree(tree, Equivalence()):
                if not self._is_operator_in_tree(tree, Implication()):
                    if not self._is_conjunction_under_disjunction(tree):
                        break
            self._rewrite_tree(tree)

            
    def _rewrite_tree(self, tree: Tree):
        if not isinstance(tree, Tree):
            return None
        if isinstance(tree.get_root(), Equivalence):
            _Equivalence_Rules.equivalence(tree)
        elif isinstance(tree.get_root(), Implication):
            _Equivalence_Rules.implication(tree)
        elif isinstance(tree.get_root(),Disjunction):
            if self._is_conjunction_under_disjunction(tree):
                _Equivalence_Rules.disjunction(tree)
        elif isinstance(tree.get_root(),Negation):
            if (isinstance(tree.get_left(), Tree)): # ¬¬a = a
                if (isinstance(tree.get_left().get_root(), Negation)):
                    tree = tree.get_left().get_left()
            elif (isinstance(tree.get_left(), Tree)): # negation only allowed on literals (¬a never ¬(a v b) etc )
                _Equivalence_Rules.negation(tree.get_root())
        if isinstance(tree, Tree):
            self._rewrite_tree(tree.get_left())
            self._rewrite_tree(tree.get_right())

    def _is_conjunction_under_disjunction(self, tree: Tree, disj=False) -> bool:
        if not isinstance(tree, Tree):
            return False
        if isinstance(tree.get_root(), Disjunction):
            return self._is_conjunction_under_disjunction(tree.get_left(), disj=True) or self._is_conjunction_under_disjunction(tree.get_right(), disj=True)
        if isinstance(tree.get_root(), Conjunction):
            if disj == True:
                return True
        return self._is_conjunction_under_disjunction(tree.get_left(), disj=disj) or self._is_conjunction_under_disjunction(tree.get_right(), disj=disj)

            
    def _is_operator_in_tree(self, tree: Tree, op: Operator) -> bool:
        if not isinstance(tree, Tree): # variable/T/F reached
            return False
        if isinstance(tree.get_root(), Operator):
            if tree.get_root().operator == op.operator:
                return True
        return self._is_operator_in_tree(tree.get_left(), op) or self._is_operator_in_tree(tree.get_right(), op)

    def naming(self, tree: Tree) -> set:
        newtree = tree
        self._add_depth(newtree,0)
        p = Polarity()
        p.polarise(newtree,pol=1)
        clauses = set()
        numberofnames = 0
        while (self._get_highest_depth(newtree) > 2):
            depth = self._get_highest_depth(newtree) -1
            nodes = self._get_nodes_at_depth(newtree, depth)
            for x in nodes:
                temp = Tree()
                if (x.pol == 1):
                    temp.set_root(Implication())
                    var = Variable("n"+str(numberofnames))
                    temp.set_left(var)
                    temp.set_right(x)
                    numberofnames=numberofnames+1
                elif (x.pol == -1):
                    temp.set_root(Implication())
                    var = Variable("n"+str(numberofnames))
                    temp.set_right(var)
                    temp.set_left(x)
                    numberofnames=numberofnames+1
                else:
                    temp.set_root(Equivalence())
                    var = Variable("n"+str(numberofnames))
                    temp.set_left(var)
                    temp.set_right(x)
                    numberofnames=numberofnames+1
                temp.depth = depth
                clauses.add(temp)
                self._replace_node_in_tree(newtree, x, var)
        clauses.add(newtree)
        return clauses

    def _replace_node_in_tree(self, tree, node, newnode):
        if not hasattr(tree, "is_tree"):
            return None
        if tree.depth > node.depth:
            return None
        if tree.get_left() != node:
            self._replace_node_in_tree(tree.get_left(), node, newnode)
        else:
            tree.set_left(newnode)
        if tree.get_right() != node:
            self._replace_node_in_tree(tree.get_right(), node, newnode)
        else:
            tree.set_right(newnode)
            
    def _get_nodes_at_depth(self, node, depth):
        if node == None:
            return []
        if node.depth > depth:
            return []
        if node.depth != depth:
            if (hasattr(node, "is_tree")):
                results = []
                left = self._get_nodes_at_depth(node.get_left(), depth) 
                right = self._get_nodes_at_depth(node.get_right(), depth)
                if left != None and left != []:
                    results.extend(left)
                if right != None and right != []:
                    results.extend(right)
                return results
            else:
                return []
        else:
            return [node]


    def _add_depth(self, node, depth):
        node.depth = depth
        if (hasattr(node, "is_tree")):
            if (node.get_left() != None):
                self._add_depth(node.get_left(), depth+1)
            if (node.get_right() != None):
                self._add_depth(node.get_right(), depth+1)

    def _get_highest_depth(self, node) -> int:
        if (hasattr(node, "is_tree")):
            left = self._get_highest_depth(node.get_left())
            right = self._get_highest_depth(node.get_right())
            if left > right:
                return left + 1
            else:
                return right + 1
        else:
            return 0

class Polarity:
    def __init__(self):
        pass

    def polarise(self, node : Tree, pol=1) -> Tree:
        node.pol = pol
        if isinstance(node, Variable) or isinstance(node, Constant):
            return None
        if isinstance(node.get_root(), Disjunction) or isinstance(node.get_root(), Conjunction):
            self.polarise(node.get_left(), pol=pol)
            self.polarise(node.get_right(), pol=pol)
        elif isinstance(node.get_root(), Negation):
            self.polarise(node.get_left(), pol=-pol)
        elif isinstance(node.get_root(), Implication):
            self.polarise(node.get_left(), pol=-pol)
            self.polarise(node.get_right(), pol=pol)
        elif isinstance(node.get_root(), Equivalence):
            self.polarise(node.get_left(), pol=0)
            self.polarise(node.get_right(), pol=0)

class _Equivalence_Rules:

    def negation(tree : Tree):
        pass
    def equivalence(tree : Tree):
        a = tree.get_left()
        b = tree.get_right()
        t1, t2, t3, t4 = Tree(), Tree(), Tree(), Tree()
        t1.set_root(Negation())
        t1.set_left(a)
        t4.set_root(Negation())
        t4.set_left(b)
        t2.set_root(Disjunction())
        t2.set_left(t1)
        t2.set_right(b)
        t3.set_root(Disjunction())
        t3.set_left(a)
        t3.set_right(t4)
        tree.set_left(t2)
        tree.set_right(t3)
        tree.set_root(Conjunction())

    def implication(tree : Tree):
        tree.set_root(Conjunction())
        temp = tree.get_left()
        temptree = Tree()
        temptree.set_root(Negation())
        temptree.set_left(temp)
        tree.set_left(temptree)

    def disjunction(tree : Tree):
        from parser import Parser
        p = Parser()
        p.print_tree(tree)
        if not isinstance(tree, Tree):
            return None
        if isinstance(tree.get_left(), Tree):
            l = tree.get_left()
            r = tree.get_right()
        elif isinstance(tree.get_right(), Tree):
            l = tree.get_right()
            r = tree.get_left()
        a = l.get_left()
        b = l.get_right()
        c = r
        # format: (a /\ b) \/ c   -->   (a \/ c) /\ (b \/ c)

        t = Tree()
        tl = Tree()
        tr = Tree()
        tree.set_left(tl)
        tree.set_right(tr)
        tree.set_root(Conjunction())
        tl.set_root(Disjunction())
        tl.set_left(a)
        tl.set_right(c)
        tr.set_root(Disjunction())
        tr.set_left(b)
        tr.set_right(c)