import xml.etree.ElementTree as XMLTree
from builtins import RuntimeError
from pathlib import Path

from log import MethodScopeLog
from statement.abstract_dir_statement import AbstractDirStatement
from statement.abstract_statement import AbstractStatement


class DirStatement(AbstractDirStatement):
    from statement.template_statement import TemplateStatement

    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement, **kargs):
        super().__init__(current_node, parent_statement, **kargs)
        self.__output_dirpath = Path()

    def current_output_dirpath(self) -> Path:
        return self.__output_dirpath

    def allows_template(self):
        return True

    def execute(self):
        with MethodScopeLog(self):
            self.__make_output_dir()

    def __make_output_dir(self):
        parent_output_dirpath = self.parent_statement().current_dir_statement().current_output_dirpath()
        self.__output_dirpath = parent_output_dirpath / self.format_str(self.current_node().attrib['path'])
        self.logger.info(f"Make dir {self.__output_dirpath}")
        self.__output_dirpath.mkdir(parents=True, exist_ok=True)

    def check_not_template_attributes(self, nb_template_attributes: int):
        assert 'path' not in self.current_node().attrib

    def post_template_run(self, template_statement: TemplateStatement):
        expected_statement = template_statement.expected_statement()
        self.__output_dirpath = expected_statement.current_output_dirpath()

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        match child_node.tag:
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
