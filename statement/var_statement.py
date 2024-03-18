import re
import xml.etree.ElementTree as XMLTree
from builtins import RuntimeError
from io import StringIO

import regex
from log import MethodScopeLog
from statement.abstract_statement import AbstractStatement
from statement.abstract_main_statement import AbstractMainStatement
from statement.random_statement import RandomStatement


class RegexFullMatch:
    def __init__(self, regex_pattern):
        if isinstance(regex_pattern, re.Pattern):
            self.__regex = regex_pattern
        else:
            self.__regex = re.compile(regex_pattern)

    def __call__(self, value_to_check: str):
        return re.fullmatch(self.__regex, value_to_check)


class VarStatement(AbstractMainStatement):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement, **kargs):
        super().__init__(current_node, parent_statement, variables=parent_statement.variables(), **kargs)
        self.__var_name = None
        self.__var_type = None
        self.__var_default = None
        self.__var_regex = None
        self.__var_value = None
        self.__io_stream = None

    def run(self):
        with MethodScopeLog(self):
            var_node = self.current_node()
            self.__var_name = var_node.attrib.get('name')
            if not re.match(regex.VAR_NAME_REGEX, self.__var_name):
                raise Exception(f"Variable name is not a valid name: '{self.__var_name}'.")
            self.__var_value = self.get_variable_value(self.__var_name)
            self.__var_type = var_node.attrib.get('type', 'str')
            var_restr = var_node.attrib.get('regex', None)
            self.__var_regex = RegexFullMatch(var_restr) if var_restr is not None else None
            if self.__var_value is None:
                self.__var_value = var_node.attrib.get('value', None)
                if self.__var_value is None:
                    if len(var_node) == 0:
                        self.__var_default = var_node.attrib.get('default', None)
                        self.__var_value = self.temgen().ui().ask_valid_var(self.__var_type, self.__var_name,
                                                                            self.__var_default, self.__var_regex)
                    else:
                        self.treat_children_nodes_of(self.current_node())
                self.__var_value = self.format_str(self.__var_value)
                self.__check_variable_value()
                self.variables().update({self.__var_name: self.__var_value})
            else:
                self.__check_variable_value()

    def __check_variable_value(self):
        #TODO use self.__var_type and self.__var_regex (if any), to check sefl.__var_value
        pass

    def treat_children_nodes_of(self, node: XMLTree.Element):
        if len(node) > 1:
            raise RuntimeError(f"Too many nodes for <{node.tag}>.")
        super().treat_children_nodes_of(node)
        self.__var_value = self.__io_stream.getvalue()

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element):
        match child_node.tag:
            case "random":
                random_statement = RandomStatement(child_node, self, self.__io_stream)
                random_statement.run()
                self.__io_stream = random_statement.io_stream()
            case _:
                super().treat_child_node(node, child_node)
