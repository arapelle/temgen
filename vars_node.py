import re
import xml.etree.ElementTree as XMLTree

import regex
from execution_context import ExecutionContext
from random_node import RandomNode
from template_tree_info import TemplateTreeInfo


class RegexFullMatch:
    def __init__(self, regex_pattern):
        if isinstance(regex_pattern, re.Pattern):
            self.__regex = regex_pattern
        else:
            self.__regex = re.compile(regex_pattern)

    def __call__(self, value_to_check: str):
        return re.fullmatch(self.__regex, value_to_check)


class VarsNode:
    @staticmethod
    def treat_vars_node(vars_node: XMLTree.Element,
                        execution_context: ExecutionContext,
                        tree_info: TemplateTreeInfo):
        if vars_node is None:
            return
        for var_node in vars_node.iterfind("var"):
            VarsNode.treat_var_node(var_node, execution_context, tree_info)

    @staticmethod
    def treat_var_node(var_node: XMLTree.Element,
                       execution_context: ExecutionContext,
                       tree_info: TemplateTreeInfo):
        var_name = var_node.attrib.get('name')
        if not re.match(regex.VAR_NAME_REGEX, var_name):
            raise Exception(f"Variable name is not a valid name: '{var_name}'.")
        if var_name not in tree_info.variables:
            var_value = var_node.attrib.get('value', None)
            if var_value is not None:
                var_value = tree_info.format_str(var_value)
            else:
                random_value_node = var_node.find("random", None)
                if random_value_node is not None:
                    var_value = RandomNode.random_string(random_value_node)
                else:
                    var_type = var_node.attrib.get('type', 'str')
                    var_default = var_node.attrib.get('default', None)
                    var_restr = var_node.attrib.get('regex', None)
                    regex_full_match = RegexFullMatch(var_restr) if var_restr is not None else None
                    var_value = execution_context.ui.ask_valid_var(var_type, var_name, var_default, regex_full_match)
            tree_info.variables[var_name] = var_value
            # print(f"{var_name}:{var_type}({var_default})={var_value}")
