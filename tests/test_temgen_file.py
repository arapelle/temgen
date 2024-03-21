import io
import random
import sys
import unittest
from pathlib import Path

from tests import config
from ui.terminal_ui import TerminalUi
from temgen import Temgen
from tests.dircmp_test_case import DirCmpTestCase


class TestTemgenFile(DirCmpTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._local_sub_dirpath = "temgen/file"
        super().setUpClass()

    def test__treat_template_xml_string__file_calls_template__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
        <var name="templates_dir" type="gstr" />
    </vars>
    <dir path="{project_root_dir}">
        <file template="{templates_dir}/temfile" template-version="1" />
    </dir>
</template>
        """
        project_root_dir = "template_xml_string__file_calls_template"
        templates_dir = config.local_templates_dirpath()
        sys.stdin = io.StringIO(f"{project_root_dir}\n{templates_dir}\nstuff\ncard")
        template_generator = Temgen(TerminalUi())
        template_generator.experimental_treat_template_xml_string(template_string,
                                                                  output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__file_copy__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
        <var name="fruit" value="Ananas" />
    </vars>
    <dir path="{project_root_dir}">
        <file path="list.txt" copy="input/data/fruits.txt" />
    </dir>
</template>
        """
        project_root_dir = "template_xml_string__file_copy"
        sys.stdin = io.StringIO(f"{project_root_dir}")
        template_generator = Temgen(TerminalUi())
        template_generator.experimental_treat_template_xml_string(template_string,
                                                                  output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)


if __name__ == '__main__':
    unittest.main()
