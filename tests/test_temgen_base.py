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
