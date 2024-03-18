import argparse
from enum import StrEnum, auto
from pathlib import Path
import re

import constants
import temgen
import regex
from ui.tkinter_ui import TkinterUi
from ui.terminal_ui import TerminalUi
from variables.variables_dict import VariablesDict


class TemgenProgram:
    class UiType(StrEnum):
        TKINTER = auto()
        TERMINAL = auto()

    def __init__(self, argv=None):
        self._args = self._parse_args(argv)
        self.__set_temgen_from_args()

    @property
    def args(self):
        return self._args

    @property
    def temgen(self):
        return self.__temgen

    def _parse_args(self, argv=None):
        prog_name = constants.PROGRAM_NAME
        prog_desc = 'A tool generating a directory architecture based on a template.'
        argparser = argparse.ArgumentParser(prog=prog_name, description=prog_desc)
        argparser.add_argument('--version', action='version',
                               version=f'{prog_name} {temgen.Temgen.VERSION}')
        argparser.add_argument('-K', f'--{TemgenProgram.UiType.TKINTER}'.lower(), action='store_const',
                               dest='ui', const=TemgenProgram.UiType.TKINTER, help='Use tkinter I/O.')
        argparser.add_argument('-T', f'--{TemgenProgram.UiType.TERMINAL}'.lower(), action='store_const',
                               dest='ui', const=TemgenProgram.UiType.TERMINAL, default='terminal',
                               help='Use terminal I/O.')
        argparser.add_argument('-C', '--custom-ui', metavar='custom_ui_cmd',
                               help='Use a custom user interface to set variables before treating them with temgen. '
                                    '(Executing custom_ui_cmd in shell is expected to use the desired custom '
                                    'interface.)')
        argparser.add_argument('-o', '--output-dir', metavar='dir_path',
                               default=Path.cwd(),
                               help='The directory where to generate the desired hierarchy (dir or file).')
        argparser.add_argument('-v', '--var', metavar='key=value', nargs='+',
                               type=TemgenProgram.__var_from_key_value_str,
                               help='Set variables.')
        argparser.add_argument('--var-file', metavar='var_json_files', nargs='+',
                               help='Set variables from a JSON files.')
        argparser.add_argument('template_path',
                               help='The template path of the file to find then to process.')
        argparser.add_argument('template_version', nargs='?',
                               help='The template version.')
        args = argparser.parse_args(argv)
        if args.ui is None:
            args.ui = TemgenProgram.UiType.TKINTER
        args.output_dir = Path(args.output_dir)
        return args

    @classmethod
    def __var_from_key_value_str(cls, key_value_str: str):
        key, value = key_value_str.split('=')
        if re.match(regex.VAR_NAME_REGEX, key):
            return key, value
        raise RuntimeError(key_value_str)

    def __set_temgen_from_args(self):
        ui = self.__build_ui_from_args()
        variables = self.__build_variables_from_args()
        self.__temgen = temgen.Temgen(ui, variables)

    def __build_ui_from_args(self):
        match self.args.ui:
            case TemgenProgram.UiType.TERMINAL:
                ui = TerminalUi()
            case TemgenProgram.UiType.TKINTER:
                ui = TkinterUi()
            case _:
                raise Exception(f"Unknown I/O: '{self.args.io}'")
        return ui

    def __build_variables_from_args(self):
        variables = VariablesDict()
        if self.args.var:
            variables.update_vars_from_dict(self.args.var)
        if self.args.var_file:
            variables.update_vars_from_files(self.args.var_file)
        if self.args.custom_ui:
            variables.update_vars_from_custom_ui(self.args.custom_ui)
        return variables

    def run(self):
        self.temgen.find_and_treat_template_file(Path(self.args.template_path),
                                                 self.args.template_version,
                                                 output_dir=self.args.output_dir)


if __name__ == '__main__':
    tgen = TemgenProgram()
    tgen.run()
