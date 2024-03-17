import xml.etree.ElementTree as XMLTree

from abc import ABC, abstractmethod

import statement.abstract_dir_statement
import statement.template_statement
from variables_dict import VariablesDict


class AbstractStatement(ABC):
    VARIABLES_LABEL = "variables"

    def __init__(self, current_node: XMLTree.Element, parent_statement, **kargs):
        assert current_node is not None
        self.__current_node = current_node
        self.__parent_statement = parent_statement
        if isinstance(self, statement.template_statement.TemplateStatement):
            self.__template_statement = self
        else:
            self.__template_statement = self.__parent_statement.template_statement()
        self.__variables = kargs.get(AbstractStatement.VARIABLES_LABEL, VariablesDict())
        assert self.__template_statement is not None and \
               isinstance(self.__template_statement, statement.template_statement.TemplateStatement)

    def parent_statement(self):
        return self.__parent_statement

    def template_statement(self):
        return self.__template_statement

    def temgen(self):
        return self.__template_statement.temgen()

    @property
    def logger(self):
        return self.temgen().logger

    def current_node(self):
        return self.__current_node

    def variables(self):
        return self.__variables

    def get_variable_value(self, variable_name, default_value=None):
        variable_value = self.__variables.get(variable_name, None)
        if variable_value is not None:
            return variable_value
        if self.__parent_statement is None:
            return default_value
        return self.__parent_statement.get_variable_value(variable_name, default_value)

    def current_dir_statement(self):
        if self.__parent_statement is None:
            return None
        return self.__parent_statement.current_dir_statement()

    def current_file_statement(self):
        if self.__parent_statement is None:
            return None
        return self.__parent_statement.current_file_statement()

    def current_main_statement(self):
        if self.__parent_statement is None:
            return None
        return self.__parent_statement.current_main_statement()

    def local_tree_root_dir_statement(self):
        assert isinstance(self.__template_statement, statement.template_statement.TemplateStatement)
        child_statement = self.__template_statement.current_child_statement()
        if isinstance(child_statement, statement.abstract_dir_statement.AbstractDirStatement):
            return child_statement
        dir_statement = self.current_dir_statement()
        if dir_statement is None or self.__template_statement == self:
            return None
        parent_dir_statement = dir_statement.parent_statement().current_dir_statement()
        while parent_dir_statement is not None:
            dir_statement = parent_dir_statement
            parent_dir_statement = dir_statement.parent_statement().current_dir_statement()
        return dir_statement

    def tree_root_dir_statement(self):
        assert isinstance(self.__template_statement, statement.template_statement.TemplateStatement)
        if self.__template_statement.parent_template_statement() is None:
            return self.local_tree_root_dir_statement()
        return self.__template_statement.parent_statement().tree_root_dir_statement()

    @abstractmethod
    def run(self):
        pass

    def format_str(self, value_str: str):
        #TODO Optimize
        vars_dict = VariablesDict()
        current_statement = self
        while current_statement is not None:
            vars_dict.update(current_statement.variables())
            current_statement = current_statement.parent_statement()
        template_filepath = self.template_statement().template_filepath()
        template_dir_var_value = template_filepath.absolute().parent if template_filepath is not None else ""
        vars_dict[VariablesDict.TEMPLATE_DIR_VARNAME] = template_dir_var_value
        return value_str.format_map(vars_dict)
