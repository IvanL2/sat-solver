from enum import Enum
import logging
from typing import Final, NamedTuple
from dpll.logic_tree import LogicTree
from dpll.types import Operator, Variable, Tautology, Contradiction

# standard logic precedence
_precedence = {'¬': 5, '∧': 4, '∨': 3, '→': 2, '↔': 1}

# Tranform multichar symbols from user input into single symbol for sake of parsing
# i.e. <-> becomes ↔
_equiv_symbols = {" ": "", "<->": "↔", "=": "↔", "->": "→", "~": "¬", "\\/": "∨",
                  "/\\": "∧", "&&": "∧", "||": "∨", "!": "¬", "F": "⊥", "T": "⊤"}

lexer_logger = logging.getLogger(f"{__name__}.lexer")
parser_logger = logging.getLogger(f"{__name__}.parser")


class TokenType(Enum):
    UNARY_OPERATOR = 1
    BINARY_OPERATOR = 2
    ATOM = 3
    START_BRACKET = 4
    END_BRACKET = 5
    EXPR = 6
    START = 7
    EOF = 8
    TRUE_START = 9


class Token():

    def __init__(self, value: str, type: TokenType):
        self.value: Final = value
        self.type: Final = type

    def __str__(self):
        return f"<Token value: '{self.value}' type: {self.type.name}>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def BinaryOp(value: str):
        return Token(value, TokenType.BINARY_OPERATOR)

    @staticmethod
    def UnaryOp(value: str):
        return Token(value, TokenType.UNARY_OPERATOR)

    @staticmethod
    def Var(value: str):
        return Token(value, TokenType.ATOM)

    @staticmethod
    def StartBracket():
        return Token('(', TokenType.START_BRACKET)

    @staticmethod
    def EndBracket():
        return Token(')', TokenType.END_BRACKET)


class ProductionRule(NamedTuple):
    # Syntax check implements a very basic SR parser; in the future should switch
    # to an SLR(1) parser with a hardcoded table that allows O(1) rule lookups
    lhs: TokenType
    rhs: list[TokenType]


grammar: list[ProductionRule] = [
        ProductionRule(TokenType.START, [TokenType.EXPR]),
        ProductionRule(TokenType.EXPR, [TokenType.EXPR, TokenType.BINARY_OPERATOR, TokenType.EXPR]),
        ProductionRule(TokenType.EXPR, [TokenType.UNARY_OPERATOR, TokenType.EXPR]),
        ProductionRule(TokenType.EXPR, [TokenType.START_BRACKET, TokenType.EXPR, TokenType.END_BRACKET]),
        ProductionRule(TokenType.EXPR, [TokenType.ATOM])
    ]


class Parser:

    @staticmethod
    def _str_list_of_enums(arr: list[TokenType]) -> str:
        """Stringifys a list of token enums for debug/verbose prints"""
        string = "["
        for x in arr:
            string = string + "<" + str(x) + ">, "
        if len(string) > 3:
            string = string[0:len(string)-2]
        string += "]"
        return string

    @staticmethod
    def lexer(exp: str) -> list[Token]:
        """Tokenises the input formula"""

        lexer_logger.info("Lexer start")

        newexp = exp
        for x in _equiv_symbols.keys():
            newexp = newexp.replace(x, _equiv_symbols[x])

        lexer_logger.debug("Replacing operator symbols with internal single character equivalents.")
        lexer_logger.debug(f"Equivalent expression: {newexp}.")

        if ">" in newexp or "<" in newexp:
            raise SyntaxError(f"Invalid character detected in expression \"{exp}\"!")

        lexeme = ""
        tokens: list[Token] = []

        for i, char in enumerate(newexp):
            match char:
                case "(" | ")":
                    tokens.append(Token.StartBracket() if char == "(" else Token.EndBracket())
                case "¬":
                    tokens.append(Token.UnaryOp(char))
                case "→" | "↔" | "∧" | "∨":
                    tokens.append(Token.BinaryOp(char))
                case _:
                    lexeme += char
                    if (i+1 < len(newexp)):  # if not EOL
                        if newexp[i+1] in ["→", "↔", "∧", "∨", "¬", "(", ")"]:  # if operator comes next
                            tokens.append(Token.Var(lexeme))
                            lexeme = ""
                    else:  # EOL
                        if lexeme != "":
                            tokens.append(Token.Var(lexeme))
        lexer_logger.info("Lexer finished")
        lexer_logger.debug(f"Tokens produced: {" ".join([str(x) for x in tokens])}")
        return tokens

    @staticmethod
    def syntax_check(tokens_with_data: list[Token]) -> bool:
        """Returns True if the given list of tokens produces a valid propositional logic expression"""
        # Basic SR parser
        parser_logger.info("Syntax check start")
        tokens = [x.type for x in tokens_with_data]
        tokens.append(TokenType.EOF)
        stack = [TokenType.TRUE_START]
        token = tokens.pop(0)
        while True:
            rule: ProductionRule | None = None
            parser_logger.debug(f"token stack len {len(stack)} {stack}")
            for b in range(1, len(stack), 1):
                applicable_rules = list(filter(lambda x: x.rhs == stack[b:len(stack)], grammar))
                parser_logger.debug(f"applicable rules: {applicable_rules}")
                if len(applicable_rules) == 1:  # If unique handle exists
                    rule = applicable_rules[0]
                    # R/R conflict with Start -> Expr, and Expr -> Expr BinOp Expr
                    # Ad hoc fix, to only reduce to start as a last resort.
                    if rule == ProductionRule(TokenType.START, [TokenType.EXPR]):
                        if not (len(stack) == 2 and len(tokens) == 0):
                            parser_logger.debug("Ignore handle (R/R conflict resolve).")
                            rule = None
                    break
            if rule is not None:
                for i in range(len(rule.rhs)):
                    _ = stack.pop()
                stack.append(rule[0])
            else:
                if (token is not TokenType.EOF):
                    stack.append(token)
                    token = tokens.pop(0)
                else:
                    parser_logger.debug(f"Syntax check fail; token stack: {stack} {[str(x) for x in tokens_with_data]}")
                    return False

            if (stack[-1] is TokenType.START and token is TokenType.EOF):
                break    # finished
        parser_logger.info("Syntax check finished")
        return True

    @staticmethod
    def construct_tree(postfix_tokens: list[Token]) -> LogicTree:
        arguments: list[LogicTree] = []
        tree = None
        for x in postfix_tokens:
            match x.value:
                case "¬":
                    node = arguments.pop()
                    tree = LogicTree(Operator.NEGATION, left=node)
                    arguments.append(tree)
                case "∧":
                    node1 = arguments.pop()
                    node2 = arguments.pop()
                    tree = LogicTree(Operator.CONJUNCTION, left=node2, right=node1)
                    arguments.append(tree)
                case "∨":
                    node1 = arguments.pop()
                    node2 = arguments.pop()
                    tree = LogicTree(Operator.DISJUNCTION, left=node2, right=node1)
                    arguments.append(tree)
                case "→":
                    node1 = arguments.pop()
                    node2 = arguments.pop()
                    tree = LogicTree(Operator.IMPLICATION, left=node2, right=node1)
                    arguments.append(tree)
                case "↔":
                    node1 = arguments.pop()
                    node2 = arguments.pop()
                    tree = LogicTree(Operator.EQUIVALENCE, left=node2, right=node1)
                    arguments.append(tree)
                case "⊤":
                    tree = LogicTree(Tautology())
                    arguments.append(tree)
                case "⊥":
                    tree = LogicTree(Contradiction())
                    arguments.append(tree)
                case _:
                    tree = LogicTree(Variable(x.value))
                    arguments.append(tree)
        final_tree = arguments.pop()
        return final_tree

    @staticmethod
    def parse(exp: str) -> LogicTree:
        tokens = Parser.lexer(exp)
        if not Parser.syntax_check(tokens):
            raise SyntaxError(f"Invalid expression in \"{str(exp)}\"!")

        postfix = infix_to_postfix(tokens)
        parser_logger.debug(f"Postfix: {str(postfix)}")

        tree = Parser.construct_tree(postfix)
        parser_logger.debug(f"Final tree: {str(tree)}")
        return tree


def infix_to_postfix(tokens: list[Token]) -> list[Token]:
    stack: list[Token] = []
    out_tokens: list[Token] = []

    for t in tokens:
        match t.type:
            case TokenType.ATOM:
                out_tokens.append(t)
            case TokenType.START_BRACKET:
                stack.append(t)
            case TokenType.END_BRACKET:
                while stack and stack[-1].type is not TokenType.START_BRACKET:
                    out_tokens.append(stack.pop())
                _ = stack.pop()
            case TokenType.UNARY_OPERATOR | TokenType.BINARY_OPERATOR:
                while stack and (stack[-1].type is not TokenType.START_BRACKET) \
                        and (_precedence[stack[-1].value] > _precedence[t.value]):
                    out_tokens.append(stack.pop())
                stack.append(t)
            case _:
                raise RuntimeError("Impossible situation; got invalid token after syntax check passed")
        parser_logger.debug(f"Stack: {str(stack)}")
        parser_logger.debug(f"Outlist: {str(out_tokens)}")
    while stack:
        out_tokens.append(stack.pop())
    return out_tokens
