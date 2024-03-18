import datetime
from typing import Mapping

from variables.variables_dict import VariablesDict
from statement.abstract_statement import AbstractStatement


class VariablesMap(Mapping):
    def __init__(self, current_statement: AbstractStatement):
        self.__statement = current_statement

    def __getitem__(self, var_name):
        if var_name[0] == '$':
            return self.__get_builtin_var_value(var_name)
        statement = self.__statement
        while statement is not None:
            value = statement.variables().get(var_name, None)
            if value is not None:
                return value
            statement = statement.parent_statement()
        raise KeyError(var_name)

    def __get_builtin_var_value(self, builtin_var_name: str):
        match builtin_var_name:
            case VariablesDict.TEMPLATE_DIR_VARNAME:
                template_filepath = self.__statement.template_statement().template_filepath()
                return template_filepath.absolute().parent if template_filepath is not None else ""
            case "$YEAR":
                return f"{datetime.date.today().year}"
            case "$MONTH":
                return f"{datetime.date.today().month:02}"
            case "$DAY":
                return f"{datetime.date.today().day:02}"
            case "$DATE_YMD":
                today = datetime.date.today()
                return f"{today.year}{today.month:02}{today.day:02}"
            case "$DATE_Y_M_D":
                today = datetime.date.today()
                return f"{today.year}-{today.month:02}-{today.day:02}"
            case _:
                raise KeyError(builtin_var_name)

    def __len__(self):
        assert False

    def __iter__(self):
        assert False
