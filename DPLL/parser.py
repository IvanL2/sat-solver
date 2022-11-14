from tree import Tree
from operators import *

precedence = {'¬': 1, '∧': 2, '∨': 3, '→': 4, '↔': 5}

class Parser:

    global precedence
    def __init__(self):
        pass
    
    def print_tree(self,tree : Tree, depth : int):
        print(tree.get_root().operator,depth)
        if hasattr(tree.get_left(), "is_tree"):
            self.print_tree(tree.get_left(), depth + 1)
        else:
            print(tree.get_left(),depth+1)
        if hasattr(tree.get_right(), "is_tree"):
            self.print_tree(tree.get_right(), depth + 1)
        else:
            if (tree.get_root().operator != "!"):
                print(tree.get_right(),depth+1)
        

    def parse(self, exp : str) -> Tree:
        infixconverter = Conversion()
        postfix = infixconverter.infixToPostfix(exp)
        print(postfix)
        operator_symbols = precedence.keys()
        depth = 0
        arguments = []
        for x in postfix:
            print("arguments",arguments,"operator",x)
            if x == "¬":
                node = arguments.pop()
                tree = Tree()
                tree.set_root(Negation())
                tree.set_left(node)
                arguments.append(tree)
            elif x == "∧":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree()
                tree.set_root(Conjunction())
                tree.set_left(node1)
                tree.set_right(node2)
                arguments.append(tree)
            elif x == "∨":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree()
                tree.set_root(Disjunction())
                tree.set_left(node1)
                tree.set_right(node2)
                arguments.append(tree)
            elif x == "→":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree()
                tree.set_root(Implication())
                tree.set_left(node1)
                tree.set_right(node2)
                arguments.append(tree)
            elif x == "↔":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree()
                tree.set_root(Equivalence())
                tree.set_left(node1)
                tree.set_right(node2)
                arguments.append(tree)
            else:
                arguments.append(x)
        final_tree = arguments.pop()
        self.print_tree(final_tree,0)
        
            

# CREDIT TO https://www.geeksforgeeks.org/convert-infix-expression-to-postfix-expression/
class Conversion:
  
    global precedence
    # Constructor to initialize the class variables
    def __init__(self):
        self.top = -1
        # This array is used a stack
        self.array = []
        # Precedence setting
        self.output = []

  
    # check if the stack is empty
    def isEmpty(self):
        return True if self.top == -1 else False
  
    # Return the value of the top of the stack
    def peek(self):
        return self.array[-1]
  
    # Pop the element from the stack
    def pop(self):
        if not self.isEmpty():
            self.top -= 1
            return self.array.pop()
        else:
            return "$"
  
    # Push the element to the stack
    def push(self, op):
        self.top += 1
        self.array.append(op)
  
    # A utility function to check is the given character
    # is operand
    def isOperand(self, ch):
        return ch.isalpha()
  
    # Check if the precedence of operator is strictly
    # less than top of stack or not
    def notGreater(self, i):
        try:
            a = precedence[i]
            b = precedence[self.peek()]
            return True if a <= b else False
        except KeyError:
            return False
  
    # The main function that
    # converts given infix expression
    # to postfix expression
    def infixToPostfix(self, exp):
  
        # Iterate over the expression for conversion
        for i in exp:
            # If the character is an operand,
            # add it to output
            if self.isOperand(i):
                self.output.append(i)
  
            # If the character is an '(', push it to stack
            elif i == '(':
                self.push(i)
  
            # If the scanned character is an ')', pop and
            # output from the stack until and '(' is found
            elif i == ')':
                while((not self.isEmpty()) and
                      self.peek() != '('):
                    a = self.pop()
                    self.output.append(a)
                if (not self.isEmpty() and self.peek() != '('):
                    return -1
                else:
                    self.pop()
  
            # An operator is encountered
            else:
                while(not self.isEmpty() and self.notGreater(i)):
                    self.output.append(self.pop())
                self.push(i)
  
        # pop all the operator from the stack
        while not self.isEmpty():
            self.output.append(self.pop())
        return "".join(self.output)


Parser().parse("(¬(a∨b)→(c∧d))↔p")