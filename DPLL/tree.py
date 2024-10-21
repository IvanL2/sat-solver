class Tree():
    __slots__ = ("value","parent","left","right","literal","pol")

    """Typical tree data structure, with parent information"""
    def __init__(self, value, parent: "Tree"=None, left: "Tree"=None, right: "Tree"=None, pol: int=None, literal: bool=False):
        self.parent = parent
        self.left = left
        if self.left != None:
            self.left.parent = self
        self.right = right
        if self.right != None:
            self.right.parent = self
        self.value = value
        self.pol = pol
        self.literal = literal

    def __deepcopy__(self: "Tree", memo) -> "Tree":
        left_tree = None
        right_tree = None
        if (self.left != None):
            left_tree = self.left.__deepcopy__(memo)
        if (self.right != None):
            right_tree = self.right.__deepcopy__(memo)
        new_tree = Tree(self.value, parent=self.parent, left=left_tree, right=right_tree)
        if hasattr(new_tree, "literal"):
            new_tree.literal = self.literal
        if hasattr(new_tree, "pol"):
            new_tree.pol = self.pol
        return new_tree

    def check_values(self: "Tree") -> bool:
        if isinstance(self.value, str): return False
        ret = True
        if (self.left != None):
            ret = self.left.check_values()
        if (self.right != None):
            ret = self.right.check_values()
        return ret
        
    @staticmethod
    def get_height(tree):
        arr = [0]
        if tree.left != None:
            arr.append(Tree.get_height(tree.left))
        if tree.right != None:
            arr.append(Tree.get_height(tree.right))
        return 1+max(arr)