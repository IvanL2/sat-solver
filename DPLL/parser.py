from tree import *
from semantics import *

precedence = {'¬': 5, '∧': 4, '∨': 3, '→': 2, '↔': 1}
equiv_symbols = {" ":"","<->":"↔","=":"↔","->":"→","~":"¬","\/":"∨","/\\":"∧","&":"∧","|":"∨","!":"¬","F":"⊥","T":"⊤"}
internal_symbol_to_icon = {">":"→", "=":"↔", "!":"¬", "&":"∧", "|":"∨"}
class Parser:

    global precedence
    
    def print_tree(tree : Tree, depth=0):
        if (depth==0):
            print("format: node, depth")
        if (tree == None):
            return
        if (tree.value == "start"):
            print("start",0)
        else:
            print(tree.value.name, depth)
        if (isinstance(tree.value, Variable) and not isinstance(tree.value, Operator)):
            return
        Parser.print_tree(tree.left, depth + 1)
        Parser.print_tree(tree.right, depth + 1)
    
    def print_exp(tree: Tree, first=True):
        if (tree.value == "start"):
            Parser.print_exp(tree.left)
            return
        if not isinstance(tree.value, Connective):
            if (tree.value.name == "!"):
                print("¬", end="")
            else:
                print(tree.value.name, end="")
            if tree.left != None:
                Parser.print_exp(tree.left, first=False)
        else:
            print("(", end="")
            if tree.left != None:
                Parser.print_exp(tree.left, first=False)
            if tree.value.name in internal_symbol_to_icon:
                print(internal_symbol_to_icon[tree.value.name], end="")
            else:
                print(tree.value.name, end="")
            if (tree.right != None):
                Parser.print_exp(tree.right, first=False)
            print(")", end="")
        if first: print()

    def parse(exp : str) -> Tree:
        infixconverter = Conversion()
        newexp = exp
        for x in equiv_symbols.keys():
            newexp = newexp.replace(x,equiv_symbols[x])
        postfix = infixconverter.infixToPostfix(newexp)
        arguments = []
        for x in postfix:
            if x == "¬":
                node = arguments.pop()
                tree = Tree(Operator.Negation(), left=node)
                arguments.append(tree)
            elif x == "∧":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Connective.Conjunction(), left=node2, right=node1)
                arguments.append(tree)
            elif x == "∨":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Connective.Disjunction(), left=node2, right=node1)
                arguments.append(tree)
            elif x == "→":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Connective.Implication(), left=node2, right=node1)
                arguments.append(tree)
            elif x == "↔":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Connective.Equivalence(), left=node2, right=node1)
                arguments.append(tree)
            elif x == "⊤":
                tree = Tree(Tautology())
                arguments.append(tree)
            elif x == "⊥":
                tree = Tree(Contradiction())
                arguments.append(tree)
            else:
                tree = Tree(Variable(x))
                arguments.append(tree)
        final_tree = Tree("start", left=arguments.pop())
        return final_tree

        
    def tree_to_infix(tree : Tree) -> str:
        string = ""
        if (isinstance(tree, Tree)):
            return Parser.tree_to_infix(tree.left) + tree.value + Parser.tree_to_infix(tree.right)
        else:
            return tree.value

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