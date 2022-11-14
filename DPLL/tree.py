class Tree():
    def __init__(self):
        self.left = None
        self.right = None
        self.root = None
        self.is_tree = True
    def is_tree(self):
        return True
    
    def get_root(self):
        return self.root
    
    def get_left(self):
        return self.left
    
    def get_right(self):
        return self.right
    
    def set_nodes(self,left,right):
        right.left = left
        self.right = right
    
    def set_root(self,root):
        self.root = root

    def set_left(self,left):
        self.left = left
    
    def set_right(self,right):
        self.right = right