import xml.etree.ElementTree as XMLTree
from pathlib import Path

from log import MethodScopeLog
from statement.abstract_main_statement import AbstractMainStatement
from statement.abstract_statement import AbstractStatement
from statement.writer.binary_to_binary_writer import BinaryToBinaryWriter
from statement.writer.binary_to_text_writer import BinaryToTextWriter
from statement.writer.text_to_binary_writer import TextToBinaryWriter
from statement.writer.text_to_text_writer import TextToTextWriter


class FileStatement(AbstractMainStatement):
    from statement.template_statement import TemplateStatement

    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractMainStatement, **kargs):
        super().__init__(current_node, parent_statement, **kargs)
        self.__output_filepath = Path()
        self.__output_file = None
        self.__output_encoding = None

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
        self.__resolve_output_filepath_and_ensure_output_dir()
        self.logger.info(f"Make file {self.__output_filepath}")
        self.__open_output_file()
        copy_attr = self.current_node().attrib.get("copy", None)
        if copy_attr is not None:
            self.__copy_file_to_output(copy_attr, self)
        else:
            assert "copy-encoding" not in self.current_node().attrib
        self.treat_children_nodes()
        self.__output_file.flush()

    def __resolve_output_filepath_and_ensure_output_dir(self):
        parent_output_dirpath = self.parent_statement().current_dir_statement().current_output_dirpath()
        self.__output_filepath = Path(parent_output_dirpath / self.format_str(self.current_node().attrib['path']))
        output_file_parent_dirpath = self.__output_filepath.parent
        if output_file_parent_dirpath != parent_output_dirpath:
            self.logger.info(f"Make dir {output_file_parent_dirpath}")
            output_file_parent_dirpath.mkdir(parents=True, exist_ok=True)

    def __open_output_file(self):
        self.__output_encoding = self.current_node().get("encoding", None)
        if self.__output_encoding == "binary":
            open_mode = "wb"
            encoding = None
        else:
            open_mode = "wt"
            encoding = self.__output_encoding
        self.__output_file = open(self.__output_filepath, mode=open_mode, encoding=encoding)

    def __copy_file_to_output(self, copy_attr: str, input_statement: AbstractStatement):
        copy_encoding_attr: str = input_statement.current_node().get("copy-encoding", None)
        copied_file_path = self.format_str(copy_attr)
        if copy_encoding_attr is not None:
            input_encoding = self.format_str(copy_encoding_attr)
        else:
            input_encoding = self.__output_encoding
        if self.__output_encoding == "binary":
            if input_encoding == "binary":
                writer = BinaryToBinaryWriter(self.__output_file)
            else:
                writer = TextToBinaryWriter(self.__output_file)
        else:
            if input_encoding == "binary":
                writer = BinaryToTextWriter(self.__output_file)
            else:
                writer = TextToTextWriter(self.__output_file)
        encoding = None if input_encoding == "binary" else input_encoding
        mode = "rb" if input_encoding == "binary" else "rt"
        with open(copied_file_path, mode=mode, encoding=encoding) as input_file:
            input_contents = input_file.read()
            writer.execute(input_contents, input_statement)

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
        input_contents = node.text if node.text is not None else ""
        input_contents_len = len(input_contents)
        if input_contents_len > 0:
            if "copy" in node.attrib:
                raise RuntimeError(f"No text is expected when copying a file.")
            if self.__output_encoding == "binary":
                writer = TextToBinaryWriter(self.__output_file)
            else:
                writer = TextToTextWriter(self.__output_file)
            writer.execute(input_contents, self)

    def check_number_of_children_nodes_of(self, node: XMLTree.Element):
        if "copy" in self.current_node().attrib and len(node) > 0:
            raise RuntimeError("No child statement is expected when copying a file.")

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        super().treat_child_node(node, child_node)
        # TODO match: <contents>
