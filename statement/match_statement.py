import re
import xml.etree.ElementTree as XMLTree

from log import MethodScopeLog
from statement.abstract_branch_statement import AbstractBranchStatement
from statement.abstract_statement import AbstractStatement


class MatchStatement(AbstractBranchStatement):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement, **kargs):
        super().__init__(current_node, parent_statement, **kargs)

    def execute(self):
        with MethodScopeLog(self):
            match_node = self.current_node()
            expr_attr = match_node.attrib['expr']
            expr_attr = self.format_str(expr_attr)
            assert match_node.text is None or len(match_node.text.strip()) == 0
            found_case_node = None
            default_case_node = None
            if len(match_node) == 0:
                raise RuntimeError("case nodes are missing in match node.")
            for case_node in match_node:
                if case_node.tag != "case":
                    raise RuntimeError(f"In 'match', bad child node type: {case_node.tag}.")
                case_value = case_node.attrib.get('value', None)
                if case_value is not None:
                    if expr_attr == self.format_str(case_value):
                        found_case_node = case_node
                        break
                    continue
                case_expr = case_node.attrib.get('expr', None)
                if case_expr is not None:
                    if re.fullmatch(self.format_str(case_expr), expr_attr):
                        found_case_node = case_node
                        break
                    continue
                if default_case_node is not None:
                    raise RuntimeError("A match node cannot have two default case nodes.")
                default_case_node = case_node
            if found_case_node:
                self.current_main_statement().treat_children_nodes_of(found_case_node)
            elif default_case_node:
                self.current_main_statement().treat_children_nodes_of(default_case_node)
