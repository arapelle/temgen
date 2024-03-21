import xml.etree.ElementTree as XMLTree

from abc import ABC, abstractmethod
from pathlib import Path
from typing import final

import statement.abstract_dir_statement
import statement.template_statement
from variables.variables_dict import VariablesDict


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
        self.__was_template_called = False

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

    def format_str(self, value_str: str):
        from variables.variables_map import VariablesMap
        return value_str.format_map(VariablesMap(self))

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

    def run(self):
        template_attr = self.current_node().get("template", None)
        version_attr = self.current_node().get('template-version', None)
        if not self.allows_template():
            template_attr_labels = []
            if template_attr is not None:
                template_attr_labels.append("'template'")
            if version_attr is not None:
                template_attr_labels.append("'template-version'")
            if len(template_attr_labels) > 0:
                forbidden_attr_str = ", ".join(template_attr_labels)
                raise RuntimeError(f"Attribute {forbidden_attr_str} found in {self.__class__.__name__}, "
                                   f"but this statement does not allow template.")
            self.execute()
        else:
            if template_attr is None:
                if version_attr is not None:
                    raise RuntimeError(f"Attribute 'template-version' found in {self.__class__.__name__}, "
                                       "but attribute 'template' is missing.")
                self.execute()
            else:
                nb_template_attributes = 1
                template_attr = self.format_str(template_attr)
                if version_attr is not None:
                    nb_template_attributes += 1
                    version_attr = self.format_str(version_attr)
                self.check_not_template_attributes(nb_template_attributes)
                template_path = self.temgen().find_template_file(Path(template_attr), version_attr)
                self.__call_template(template_path)

    def allows_template(self):
        return False

    def check_not_template_attributes(self, nb_template_attributes: int):
        pass

    @abstractmethod
    def execute(self):
        pass

    @final
    def __call_template(self, template_path: Path):
        with open(template_path, 'r') as template_file:
            data_tree = XMLTree.parse(template_file)
        from statement.template_statement import TemplateStatement
        template_statement = TemplateStatement(data_tree.getroot(), self,
                                               variables=self.variables(),
                                               template_filepath=template_path)
        self.pre_template_run(template_statement)
        template_statement.run()
        self.__was_template_called = True
        assert isinstance(template_statement.expected_statement(), self.__class__)
        self.post_template_run(template_statement)

    def was_template_called(self):
        return self.__was_template_called

    def pre_template_run(self, template_statement):
        pass

    def post_template_run(self, template_statement):
        pass
