from enum import Enum
from typing import Set

from dpll.tree import Tree
from dpll.semantics import Operator, Variable, Tautology, Contradiction

import dpll.verbosity_config as verbosity_config

precedence = {'¬': 5, '∧': 4, '∨': 3, '→': 2, '↔': 1}

# Tranform multichar symbols from user input into single symbol for sake of parsing
# i.e. <-> becomes ↔
equiv_symbols = {" ": "", "<->": "↔", "=": "↔", "->": "→", "~": "¬", "\\/": "∨",
                 "/\\": "∧", "&&": "∧", "||": "∨", "!": "¬", "F": "⊥", "T": "⊤"}


class TokenType(Enum):
    UNARY_OPERATOR = 1
    BINARY_OPERATOR = 2
    LITERAL = 3
    START_BRACKET = 4
    END_BRACKET = 5
    EXPR = 6
    START = 7
    EOF = 8
    _TRUE_START = 9


class Token():

    def __init__(self, value: str, type: TokenType):
        self.value = value
        self.type = type

    def __str__(self):
        return f"<Token value: '{self.value}' type: {self.type.name}>"

    def BinaryOp(value: str):
        return Token(value, TokenType.BINARY_OPERATOR)

    def UnaryOp(value: str):
        return Token(value, TokenType.UNARY_OPERATOR)

    def Var(value: str):
        return Token(value, TokenType.LITERAL)

    def StartBracket():
        return Token('(', TokenType.START_BRACKET)

    def EndBracket():
        return Token(')', TokenType.END_BRACKET)


grammar = [[TokenType.START, [TokenType.EXPR]],
           [TokenType.EXPR, [TokenType.EXPR, TokenType.BINARY_OPERATOR, TokenType.EXPR]],
           [TokenType.EXPR, [TokenType.UNARY_OPERATOR, TokenType.EXPR]],
           [TokenType.EXPR, [TokenType.START_BRACKET, TokenType.EXPR, TokenType.END_BRACKET]],
           [TokenType.EXPR, [TokenType.LITERAL]]]


class Parser:

    def __str_list_of_enums__(arr: list[TokenType]) -> str:
        """Stringifys a list of token enums for debug/verbose prints"""
        string = "["
        for x in arr:
            string = string + "<" + str(x) + ">, "
        if len(string) > 3:
            string = string[0:len(string)-2]
        string += "]"
        return string

    def lexer(exp: str, verbose: bool = False) -> list[Token]:
        """Tokenises the input formula"""

        if (verbose):
            print("Lexer start")

        newexp = exp
        for x in equiv_symbols.keys():
            newexp = newexp.replace(x, equiv_symbols[x])

        if (verbose):
            print("Replacing operator symbols with internal single character equivalents.")
            print(f"Equivalent expression: {newexp}.")

        if ">" in newexp or "<" in newexp:
            raise SyntaxError(f"Invalid character detected in expression \"{exp}\"!")

        lexeme = ""
        tokens = []
        binary_ops = ["→", "↔", "∧", "∨"]
        unary_ops = ["¬"]
        brackets = ["(", ")"]

        for i, char in enumerate(newexp):
            if char in brackets:
                tokens.append(Token.StartBracket() if char == "(" else Token.EndBracket())
            elif char in unary_ops:
                tokens.append(Token.UnaryOp(char))
            elif char in binary_ops:
                tokens.append(Token.BinaryOp(char))
            else:
                lexeme += char
                if (i+1 < len(newexp)):
                    if newexp[i+1] in binary_ops or newexp[i+1] in unary_ops or newexp[i+1] in brackets:  # if operator comes next
                        tokens.append(Token.Var(lexeme))
                        lexeme = ""
                else:  # EOF
                    if lexeme != "":
                        tokens.append(Token.Var(lexeme))
        if verbose:
            print("Lexer finished")
        return tokens

    def syntax_check(tokens_with_data: list[Token], verbose: bool = False) -> bool:
        """Returns True if the given list of tokens produces a valid propositional logic expression"""
        # Basic SR parser
        if verbose:
            print("Syntax check start")
        tokens = [x.type for x in tokens_with_data]
        tokens.append(TokenType.EOF)
        stack = [TokenType._TRUE_START]
        token = tokens.pop(0)
        while 1:
            rule = None
            for b in range(1, len(stack), 1):
                rules_st_a_to_b = list(filter(lambda x: x[1] == stack[b:len(stack)], grammar))
                if len(rules_st_a_to_b) == 1:  # If unique handle exists
                    # R/R conflict with Start -> Expr, and Expr -> Expr BinOp Expr
                    # Ad hoc fix, to only reduce to start as a last resort.
                    if rules_st_a_to_b[0][1] == [TokenType.EXPR] and rules_st_a_to_b[0][0] == TokenType.START:
                        if len(stack) == 2 and len(tokens) == 0:
                            rule = rules_st_a_to_b[0]
                        else:
                            if verbose:
                                print("Ignore handle (R/R conflict resolve) to avoid matching start rule before last iteration.")
                            rule = None
                    else:
                        rule = rules_st_a_to_b[0]
                    break
            if rule is not None:
                for i in range(len(rule[1])):
                    stack.pop()
                stack.append(rule[0])
            else:
                if (token != TokenType.EOF):
                    stack.append(token)
                    token = tokens.pop(0)
                else:
                    print("ERROR, token stack:", stack, [str(x) for x in tokens_with_data])
                    return False

            if (stack[-1] == TokenType.START and token == TokenType.EOF):
                break    # finished
        if verbose:
            print("Syntax check finished")
        return True

    def parse(exp: str, verbose: bool = False) -> Tree:
        tokens = Parser.lexer(exp, verbose=(verbose and verbosity_config.LEXER_VERBOSE))
        if verbose and verbosity_config.LEXER_VERBOSE:
            print("Parsed into tokens: ", " ".join([str(x) for x in tokens]))
        if not Parser.syntax_check(tokens, verbose=(verbose and verbosity_config.SYNTAX_VERBOSE)):
            raise SyntaxError(f"Invalid expression in \"{exp}\"!")
        infixconverter = Conversion()
        postfix = infixconverter.infixToPostfix(tokens)
        if verbose and verbosity_config.LEXER_VERBOSE:
            print("Postfix: ", " ".join([str(x) for x in postfix]))
        arguments = []
        for x in postfix:
            if x.value == "¬":
                node = arguments.pop()
                tree = Tree(Operator.NEGATION, left=node)
                arguments.append(tree)
            elif x.value == "∧":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Operator.CONJUNCTION, left=node2, right=node1)
                arguments.append(tree)
            elif x.value == "∨":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Operator.DISJUNCTION, left=node2, right=node1)
                arguments.append(tree)
            elif x.value == "→":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Operator.IMPLICATION, left=node2, right=node1)
                arguments.append(tree)
            elif x.value == "↔":
                node1 = arguments.pop()
                node2 = arguments.pop()
                tree = Tree(Operator.EQUIVALENCE, left=node2, right=node1)
                arguments.append(tree)
            elif x.value == "⊤":
                tree = Tree(Tautology)
                arguments.append(tree)
            elif x.value == "⊥":
                tree = Tree(Contradiction)
                arguments.append(tree)
            else:
                tree = Tree(Variable(x.value))
                arguments.append(tree)
        final_tree = arguments.pop()
        if verbose:
            print("Final tree: ", end="")
            Parser.print_exp(final_tree)
        return final_tree

    def check_no_tree_as_value(tree: Tree) -> bool:
        if tree is None:
            return True
        return not isinstance(tree.value, Tree) and (Parser.check_no_tree_as_value(tree.left)) and (Parser.check_no_tree_as_value(tree.right))

    def tree_to_infix(tree: Tree) -> str:
        if (isinstance(tree, Tree)):
            return Parser.tree_to_infix(tree.left) + tree.value + Parser.tree_to_infix(tree.right)
        else:
            return tree.value

    def print_tree(tree: Tree, depth: int = 0):
        if depth == 0:
            print("format: node, depth")
        if tree is None:
            return
        else:
            print(tree.value.name, depth)
        if (isinstance(tree.value, Variable) and not isinstance(tree.value, Operator)):
            return
        Parser.print_tree(tree.left, depth + 1)
        Parser.print_tree(tree.right, depth + 1)

    def print_exp(tree: Tree, first: bool = True):
        if tree is None:
            return
        if isinstance(tree.value, Operator):
            if (tree.value == Operator.NEGATION):
                print("¬", end="")
                Parser.print_exp(tree.left, first=False)
            else:
                print("(", end="")
                Parser.print_exp(tree.left, first=False)
                print(str(tree.value), end="")
                Parser.print_exp(tree.right, first=False)
                print(")", end="")
        else:
            print(tree.value.name, end="")
        if first:
            print()

    def print_exp_return_str(tree: Tree) -> str:
        if tree is None:
            return
        if isinstance(tree.value, Operator):
            if (tree.value == Operator.NEGATION):
                return "¬" + Parser.print_exp_return_str(tree.left)
            else:
                return "(" + Parser.print_exp_return_str(tree.left) + str(tree.value) + Parser.print_exp_return_str(tree.right) + ")"
        else:
            return tree.value.name

    def get_variable_names(tree: Tree) -> Set[str]:
        if tree.left is None and tree.right is None:
            return {tree.value.name}
        names = set()
        if tree.left is not None:
            names = names.union(Parser.get_variable_names(tree.left))
        if tree.right is not None:
            names = names.union(Parser.get_variable_names(tree.right))
        return names


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
    def isOperand(self, ch: Token):
        return ch.type == TokenType.LITERAL

    # Check if the precedence of operator is strictly
    # less than top of stack or not
    def notGreater(self, i):
        try:
            a = precedence[i.value]
            b = precedence[self.peek().value]
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
            elif i.value == '(':
                self.push(i)

            # If the scanned character is an ')', pop and
            # output from the stack until and '(' is found
            elif i.value == ')':
                while((not self.isEmpty()) and
                      self.peek().value != '('):
                    a = self.pop()
                    self.output.append(a)
                if (not self.isEmpty() and self.peek().value != '('):
                    return -1
                else:
                    self.pop()

            # An operator is encountered
            else:
                if i.value != "¬":    # ad hoc fix
                    while(not self.isEmpty() and self.notGreater(i)):
                        self.output.append(self.pop())
                self.push(i)

        # pop all the operator from the stack
        while not self.isEmpty():
            self.output.append(self.pop())
        return self.output
