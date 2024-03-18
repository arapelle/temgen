import xml.etree.ElementTree as XMLTree
from builtins import RuntimeError

from log import MethodScopeLog
from statement.abstract_statement import AbstractStatement
from statement.abstract_main_statement import AbstractMainStatement
from statement.var_statement import VarStatement


class VarsStatement(AbstractMainStatement):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement, **kargs):
        super().__init__(current_node, parent_statement, variables=parent_statement.variables(), **kargs)

    def run(self):
        with MethodScopeLog(self):
            self.treat_children_nodes_of(self.current_node())

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        match child_node.tag:
            case "var":
                var_statement = VarStatement(child_node, self)
                var_statement.run()
            case "if":
                from statement.if_statement import IfStatement
                if_statement = IfStatement(child_node, self)
                if_statement.run()
            case "match":
                from statement.match_statement import MatchStatement
                match_statement = MatchStatement(child_node, self)
                match_statement.run()
            case _:
                super().treat_child_node(node, child_node)
