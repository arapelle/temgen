import xml.etree.ElementTree as XMLTree
from abc import ABC
from typing import final

from statement.abstract_statement import AbstractStatement


class AbstractMainStatement(AbstractStatement, ABC):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement, **kargs):
        super().__init__(current_node, parent_statement, **kargs)
        self.__children_treated = False

    @final
    def run(self):
        super().run()
        if not self.__children_treated:
            self.treat_children_nodes()

    def current_main_statement(self):
        return self

    def treat_children_nodes(self):
        self.treat_children_nodes_of(self.current_node())
        self.__children_treated = True

    @final
    def treat_children_nodes_of(self, node: XMLTree.Element):
        self.check_number_of_children_nodes_of(node)
        if len(node) == 0:
            self.treat_text_of(node)
        else:
            for child_node in node:
                self.treat_child_node(node, child_node)

    def check_number_of_children_nodes_of(self, node: XMLTree.Element):
        pass

    def treat_text_of(self, node: XMLTree.Element):
        if node.text is not None:
            node_text = node.text.strip()
            if len(node_text) > 0:
                raise RuntimeError(f"In '{node.tag}', text is expected to be empty.")

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        raise RuntimeError(f"In '{node.tag}', bad child node type: {child_node.tag}.")
