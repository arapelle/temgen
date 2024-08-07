import xml.etree.ElementTree as XMLTree

from statement.abstract_statement import AbstractStatement
from statement.abstract_main_statement import AbstractMainStatement
from statement.var_statement import VarStatement


class VarsStatement(AbstractMainStatement):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement, **kargs):
        super().__init__(current_node, parent_statement, variables=parent_statement.variables(), **kargs)
        if isinstance(parent_statement, VarsStatement):
            self.__ui_variables = parent_statement.__ui_variables.clone() if parent_statement.__ui_variables else None
        else:
            self.__ui_variables = None

    def allows_template(self):
        return True

    def extends_template(self):
        return True

    def execute(self):
        ui = self.current_node().get("ui")
        if ui:
            ui_format_attr = self.current_node().get("ui-format", "raw")
            match ui_format_attr:
                case "raw":
                    pass
                case "format":
                    ui = self.vformat(ui)
                case _:
                    raise RuntimeError(f"Unknown format for ui attribute: '{ui_format_attr}'")
            if self.__ui_variables:
                self.__ui_variables |= self.temgen().call_ui(ui, self)
            else:
                self.__ui_variables = self.temgen().call_ui(ui, self)

    def treat_child_node(self, node: XMLTree.Element, child_node: XMLTree.Element, current_statement):
        match child_node.tag:
            case "var":
                var_statement = VarStatement(child_node, self, self.__ui_variables)
                var_statement.run()
            case "if":
                from statement.if_statement import IfStatement
                if_statement = IfStatement(child_node, self)
                if_statement.run()
            case "match":
                from statement.match_statement import MatchStatement
                match_statement = MatchStatement(child_node, self)
                match_statement.run()
            case "vars":
                vars_statement = VarsStatement(child_node, self)
                vars_statement.run()
            case _:
                super().treat_child_node(node, child_node, current_statement)
