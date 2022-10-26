from typing import List

from lark import Tree, Visitor


class GenericRule(Visitor):

    def run_rule(self, fname: str, tree: Tree) -> List:
    
        # pylint: disable=attribute-defined-outside-init
        self.fname = fname
        self.results: List = []
        self.original_tree = tree
        self.visit(tree)
        return self.results
