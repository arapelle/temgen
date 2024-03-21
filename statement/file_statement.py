import xml.etree.ElementTree as XMLTree
from pathlib import Path

from log import MethodScopeLog
from statement.abstract_main_statement import AbstractMainStatement


class FileStatement(AbstractMainStatement):
    from statement.template_statement import TemplateStatement

    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractMainStatement, **kargs):
        super().__init__(current_node, parent_statement, **kargs)
        self.__output_filepath = Path()
        self.__output_file = None

    def __del__(self):
        if self.__output_file is not None:
            self.__output_file.close()
            self.__output_file = None

    def current_file_statement(self):
        return self

    def current_output_filepath(self):
        return self.__output_filepath

    def current_output_file(self):
        return self.__output_file

    def extract_current_output_file(self):
        output_file = self.__output_file
        self.__output_file = None
        return output_file

    def allows_template(self):
        return True

    def execute(self):
        with MethodScopeLog(self):
            self.__make_output_file()

    def __make_output_file(self):
        parent_output_dirpath = self.parent_statement().current_dir_statement().current_output_dirpath()
        self.__output_filepath = Path(parent_output_dirpath / self.format_str(self.current_node().attrib['path']))
        output_file_parent_dirpath = self.__output_filepath.parent
        if output_file_parent_dirpath != parent_output_dirpath:
            self.logger.info(f"Make dir {output_file_parent_dirpath}")
            output_file_parent_dirpath.mkdir(parents=True, exist_ok=True)
        open_mode = "w"
        self.logger.info(f"Make file {self.__output_filepath}")
        self.__output_file = open(self.__output_filepath, open_mode)
        self.treat_children_nodes()
        self.__output_file.flush()

    def check_not_template_attributes(self, nb_template_attributes: int):
        assert 'path' not in self.current_node().attrib

    def post_template_run(self, template_statement: TemplateStatement):
        expected_statement = template_statement.expected_statement()
        self.__output_filepath = expected_statement.current_output_filepath()
        self.__output_file = expected_statement.extract_current_output_file()
        self.treat_children_nodes()
        self.__output_file.flush()
        self.__output_file.close()
        self.__output_file = None

    def treat_text_of(self, node: XMLTree.Element):
        copy_attr = node.attrib.get('copy')
        if copy_attr is None:
            text: str = "" if node.text is None else FileStatement.strip_text(node.text)
        else:
            copied_file_path = self.format_str(copy_attr)
            with open(copied_file_path, 'r') as copied_file:
                text: str = copied_file.read()
        format_attr = node.attrib.get('format', "format")
        format_attr_list: list = [self.format_str(fstr) for fstr in format_attr.split('|')]
        if len(format_attr_list) == 0 or "format" in format_attr_list:
            text = self.format_str(text)
        elif "raw" in format_attr_list:
            pass
        self.__output_file.write(text)

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        super().treat_child_node(node, child_node)
        # TODO match: <contents>

    @staticmethod
    def strip_text(text: str):
        text = text.lstrip()
        if len(text) > 0:
            idx = 0
            while " \t".find(text[-(idx + 1)]) != -1:
                idx = idx + 1
            if idx > 0:
                text = text[:-idx]
        return text
