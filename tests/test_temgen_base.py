import io
import sys
from pathlib import Path

from ui.terminal_ui import TerminalUi
from temgen import Temgen
from tests.dircmp_test_case import DirCmpTestCase


class TestTemgenBase(DirCmpTestCase):
    def _test__treat_template_xml_string__ok(self,
                                             template_string: str,
                                             project_root_dir: str,
                                             input_parameters):
        input_parameters_str = "\n".join(input_parameters)
        sys.stdin = io.StringIO(f"{project_root_dir}\n{input_parameters_str}")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string, output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def _test__treat_template_xml_string__exception(self,
                                                    template_string: str,
                                                    project_root_dir: str,
                                                    input_parameters):
        input_parameters_str = "\n".join(input_parameters)
        sys.stdin = io.StringIO(f"{project_root_dir}\n{input_parameters_str}")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string, output_dir=Path(self._output_dirpath))
        self.fail()

    def _run__treat_template_xml_string__file_contents__ok(self,
                                                           file_contents: str,
                                                           project_root_dir: str,
                                                           input_parameters):
        template_string = f"""<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
    </vars>
    <dir path="{project_root_dir}">
        <file path="data.txt">
{file_contents}
        </file>
    </dir>
</template>
        """
        input_parameters_str = "\n".join(input_parameters)
        sys.stdin = io.StringIO(f"{project_root_dir}\n{input_parameters_str}")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string, output_dir=Path(self._output_dirpath))
        with open(f"{self._output_dirpath}/{project_root_dir}/data.txt") as output_file:
            return output_file.read().strip()
