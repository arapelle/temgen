import xml.etree.ElementTree as XMLTree
from pathlib import Path

import constants
from log import MethodScopeLog
from statement.abstract_dir_statement import AbstractDirStatement
from statement.abstract_statement import AbstractStatement
from statement.vars_statement import VarsStatement


class TemplateStatement(AbstractDirStatement):
    from temgen import Temgen

    STATEMENT_LABEL = "template"

    TEMGEN_LABEL = constants.LOWER_PROGRAM_NAME
    TEMPLATE_FILEPATH_LABEL = "template_filepath"
    OUTPUT_DIRPATH_LABEL = "output_dirpath"

    def __init__(self, current_node: XMLTree.Element, caller_statement: AbstractStatement | None, **kargs):
        if current_node.tag != self.STATEMENT_LABEL:
            raise RuntimeError(f"Root node must be '{self.STATEMENT_LABEL}'!")
        self.__caller_statement = caller_statement
        parent_statement = None
        if self.__caller_statement is not None:
            parent_statement = self.__caller_statement.parent_statement()
            self.__parent_template_statement = parent_statement.template_statement()
            assert self.__parent_template_statement is not None
            self.__temgen = self.__parent_template_statement.temgen()
            self.__output_dirpath = parent_statement.current_dir_statement().current_output_dirpath()
        else:
            self.__parent_template_statement = None
            self.__temgen = kargs[TemplateStatement.TEMGEN_LABEL]
            self.__output_dirpath = kargs[TemplateStatement.OUTPUT_DIRPATH_LABEL]
        super().__init__(current_node, parent_statement, **kargs)
        assert self.parent_statement() == parent_statement
        self.__template_filepath = kargs.get(TemplateStatement.TEMPLATE_FILEPATH_LABEL, None)
        assert isinstance(self.__template_filepath, Path) or self.__template_filepath is None
        self.__current_child_statement = None
        self.__expected_statement = None

    def parent_template_statement(self):
        return self.__parent_template_statement

    def root_parent_template_statement(self):
        if self.__parent_template_statement is None:
            return self
        return self.__parent_template_statement.root_parent_template_statement()

    def temgen(self) -> Temgen:
        return self.__temgen

    def template_filepath(self):
        return self.__template_filepath

    def current_output_dirpath(self) -> Path:
        return self.__output_dirpath

    def current_child_statement(self):
        return self.__current_child_statement

    def expected_statement(self):
        return self.__expected_statement

    def run(self):
        with MethodScopeLog(self):
            self.__check_temgen_version()
            vars_node = self.current_node().find("vars")
            if vars_node is not None:
                self.__current_child_statement = VarsStatement(vars_node, self)
                self.__current_child_statement.run()
            self.treat_children_nodes_of(self.current_node())
            self.__current_child_statement = None

    def __check_temgen_version(self):
        from temgen import Temgen
        import semver
        min_version = self.current_node().get("temgen-min-version", None)
        max_version = self.current_node().get("temgen-max-version", None)
        if min_version is None and max_version is None:
            return
        if min_version is not None:
            min_version = semver.Version.parse(min_version)
            max_version = semver.Version.parse(max_version) if max_version is not None else Temgen.VERSION
        else:
            min_version = Temgen.VERSION
            max_version = semver.Version.parse(max_version)
        if min_version > max_version:
            raise RuntimeError("temgen-min-version should not be greater than temgen-max-version: "
                                f"min: {min_version}, max: {max_version}")
        if Temgen.VERSION < min_version:
            raise RuntimeError("temgen is not compatible with the expected min version: "
                               f"{Temgen.VERSION} (min: {min_version})")
        if Temgen.VERSION > max_version:
            raise RuntimeError("temgen is not compatible with the expected max version: "
                               f"{Temgen.VERSION} (max: {max_version})")

    def treat_children_nodes_of(self, node: XMLTree.Element):
        if node == self.current_node():
            limit = 2 if node.find("vars") is not None else 1
            if len(node) > limit:
                raise RuntimeError("Too many nodes under <template>.")
        super().treat_children_nodes_of(node)

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        if child_node.tag == "vars":
            if node == self.current_node():
                return
        if self.__caller_statement is not None and node == self.current_node():
            expected_tag = self.__caller_statement.current_node().tag
            if child_node.tag != expected_tag:
                raise RuntimeError(f"Unexpected node ({child_node.tag}) under <template>. "
                                   f"Expected: {expected_tag}.")
        super().treat_child_node(node, child_node)
        assert self.__current_child_statement is not None
        if self.__caller_statement is not None and node == self.current_node():
            self.__expected_statement = self.__current_child_statement
        self.__current_child_statement = None

    def _create_dir_statement(self, node: XMLTree.Element, child_node: XMLTree.Element):
        dir_statement = super()._create_dir_statement(node, child_node)
        if node == self.current_node():
            self.__current_child_statement = dir_statement
        return dir_statement

    def _create_file_statement(self, node: XMLTree.Element, child_node: XMLTree.Element):
        file_statement = super()._create_file_statement(node, child_node)
        if node == self.current_node():
            self.__current_child_statement = file_statement
        return file_statement
