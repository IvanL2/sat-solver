class Tree():
    """Typical tree data structure, with parent information"""
    def __init__(self, value, parent: "Tree"=None, left: "Tree"=None, right: "Tree"=None):
        self.parent = parent
        self.left = left
        if self.left != None:
            self.left.parent = self
        self.right = right
        if self.right != None:
            self.right.parent = self
        self.value = value

    @staticmethod
    def get_height(tree):
        arr = [0]
        if tree.left != None:
            arr.append(tree.right.get_height(tree.left))
        if tree.right != None:
            arr.append(tree.right.get_height(tree.right))
        return 1+max(arr)