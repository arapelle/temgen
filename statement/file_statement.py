import xml.etree.ElementTree as XMLTree
from pathlib import Path

from statement.abstract_main_statement import AbstractMainStatement


class FileStatement(AbstractMainStatement):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractMainStatement, **kargs):
        super().__init__(current_node, parent_statement, **kargs)
        self.__output_filepath = Path()
        self.__output_file = None

    def current_file_statement(self):
        return self

    def current_output_filepath(self):
        return self.__output_filepath

    def current_output_file(self):
        return self.__output_file

    def run(self):
        parent_output_dirpath = self.parent_statement().current_dir_statement().current_output_dirpath()
        self.__output_filepath = Path(parent_output_dirpath / self.format_str(self.current_node().attrib['path']))
        self.__output_filepath.parent.mkdir(parents=True, exist_ok=True)
        open_mode = "w"
        with open(self.__output_filepath, open_mode) as file:
            self.__output_file = file
            self.__output_file.write(self.__file_text(self.current_node()))
            self.treat_children_nodes_of(self.current_node())
        self.__output_file = None

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        super().treat_child_node(node, child_node)
        # TODO match: <contents>

    def __file_text(self, file_node: XMLTree.Element):
        copy_attr = file_node.attrib.get('copy')
        if copy_attr is None:
            text: str = "" if file_node.text is None else FileStatement.strip_text(file_node.text)
        else:
            copy_attr = self.format_str(copy_attr)
            with open(copy_attr) as copied_file:
                text: str = copied_file.read()
        format_attr = file_node.attrib.get('format', "format")
        format_attr_list: list = [self.format_str(fstr) for fstr in format_attr.split('|')]
        if len(format_attr_list) == 0 or "format" in format_attr_list:
            text = self.format_str(text)
        elif "raw" in format_attr_list:
            pass
        return text

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
