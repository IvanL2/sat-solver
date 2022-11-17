## Rundown of modules

parser.Parser     converts a propositional formula expression i.e. "a\/b->c" into an AST, provided by the Tree module.
tree.Tree         tree structure for the AST
cnf_transformer.Transformer   takes an AST and by using equivalence rules rewrites into a set of clauses.
pure_literal_eliminator.Eliminator   Uses pure literal elimination to optimise number of clauses.

Todo:   Unit Propagation to implement DPLL unit propagation to finalise results.
        Tautology elimination (i.e. T \/ p)
        fix any parsing bugs
        fix cnf producing invalid clauses
