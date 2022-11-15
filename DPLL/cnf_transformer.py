from tree import Tree
from parser import Variable
from operators import *

class Transformer:
    def __init__(self):
        pass
    
    def transform(self, tree : Tree):
        newtree = tree

        self._add_depth(newtree,0)
        p = Polarity()
        p.polarise(newtree,pol=1)
        clauses = set()
        numberofnames = 0
        while (self._get_highest_depth(newtree) > 1):
            depth = self._get_highest_depth(newtree) -1
            print("depth",depth)
            nodes = self._get_nodes_at_depth(newtree, depth)
            print("nodes",nodes)
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
                print(x)
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
        if isinstance(node, Variable):
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