from parser import Parser
from tree import Tree

ast = Parser.parse("(a->b)\/(c<->d)")
Tree.add_depth_information(ast)
Parser.print_tree(ast)