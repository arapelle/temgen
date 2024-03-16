import xml.etree.ElementTree as XMLTree
from builtins import RuntimeError
from pathlib import Path

from log import MethodScopeLog
from statement.abstract_dir_statement import AbstractDirStatement
from statement.abstract_statement import AbstractStatement


class DirStatement(AbstractDirStatement):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement, **kargs):
        super().__init__(current_node, parent_statement, **kargs)
        self.__output_dirpath = Path()

    def run(self):
        with MethodScopeLog(self):
            template_path = self.current_node().get('template', None)
            if template_path is None:
                self.__make_output_dir()
            else:
                self.__run_template(template_path)
            self.treat_children_nodes_of(self.current_node())

    def __make_output_dir(self):
        parent_output_dirpath = self.parent_statement().current_dir_statement().current_output_dirpath()
        self.__output_dirpath = parent_output_dirpath / self.format_str(self.current_node().attrib['path'])
        self.logger.info(f"Make dir {self.__output_dirpath}")
        self.__output_dirpath.mkdir(parents=True, exist_ok=True)

    def __run_template(self, template_path):
        assert 'path' not in self.current_node().attrib
        template_path = Path(self.format_str(template_path))
        version_attr = self.current_node().get('template-version', None)
        if version_attr:
            version_attr = self.format_str(version_attr)
        template_path = self.temgen().find_template_file(template_path, version_attr)
        from statement.template_statement import TemplateStatement
        with open(template_path, 'r') as template_file:
            data_tree = XMLTree.parse(template_file)
        template_statement = TemplateStatement(data_tree.getroot(), self,
                                               variables=self.variables(),
                                               template_filepath=template_path)
        template_statement.run()
        expected_statement = template_statement.expected_statement()
        assert isinstance(expected_statement, self.__class__)
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

    def current_output_dirpath(self) -> Path:
        return self.__output_dirpath
