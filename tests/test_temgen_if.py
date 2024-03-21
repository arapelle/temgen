import io
import random
import sys
import unittest
from pathlib import Path

from ui.terminal_ui import TerminalUi
from temgen import Temgen
from tests.dircmp_test_case import DirCmpTestCase


class TestTemgenIf(DirCmpTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._local_sub_dirpath = "temgen/if"
        super().setUpClass()

    @staticmethod
    def if_valid_cmp_str__template_string():
        return """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
        <var name="first_if" type="gstr" />
        <var name="second_if" type="gstr" />
    </vars>
    <dir path="{project_root_dir}">
        <if expr="'{first_if}' == 'yes'">
            <file path="first_if_alone.txt">data</file>
        </if>
        <if expr="'{first_if}' == 'yes'">
            <if expr="'{second_if}' == 'yes'">
                <file path="second_if_alone.txt">data</file>
            </if>
        </if>
        <if expr="match(r'[a-z]+', '{second_if}')">
            <file path="expr_match.txt">data</file>
        </if>
        <if expr="'{first_if}' == 'yes' and '{second_if}' == 'yes'">
            <file path="and.txt">data</file>
        </if>
        <if expr="'{first_if}' == 'yes'">
            <then>
                <file path="first_then.txt">data</file>
            </then>
            <else>
                <file path="first_else.txt">data</file>
            </else>
        </if>
        <if expr="'{first_if}' == 'yes'">
            <then>
                <if expr="'{second_if}' == 'yes'">
                    <then>
                        <file path="second_then.txt">data</file>
                    </then>
                    <else>
                        <file path="second_else.txt">data</file>
                    </else>
                </if>
            </then>
        </if>
    </dir>
</template>
        """

    def test__treat_template_xml_string__if_valid_cmp_str_yes_yes__ok(self):
        template_string = self.if_valid_cmp_str__template_string()
        project_root_dir = "template_xml_string__if_valid_cmp_str_yes_yes"
        sys.stdin = io.StringIO(f"{project_root_dir}\nyes\nyes")
        template_generator = Temgen(TerminalUi())
        template_generator.experimental_treat_template_xml_string(template_string,
                                                                  output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__if_valid_cmp_str_yes_no__ok(self):
        template_string = self.if_valid_cmp_str__template_string()
        project_root_dir = "template_xml_string__if_valid_cmp_str_yes_no"
        sys.stdin = io.StringIO(f"{project_root_dir}\nyes\nno")
        template_generator = Temgen(TerminalUi())
        template_generator.experimental_treat_template_xml_string(template_string,
                                                                  output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__if_valid_cmp_str_NO_NO__ok(self):
        template_string = self.if_valid_cmp_str__template_string()
        project_root_dir = "template_xml_string__if_valid_cmp_str_NO_NO"
        sys.stdin = io.StringIO(f"{project_root_dir}\nNO\nNO")
        template_generator = Temgen(TerminalUi())
        template_generator.experimental_treat_template_xml_string(template_string,
                                                                  output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__if_invalid_two_then__exception(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
        <var name="if_expr" type="gstr" />
    </vars>
    <dir path="{project_root_dir}">
        <if expr="'{if_expr}' == 'yes'">
            <then>
                <file path="then.txt" />
            </then>
            <else>
                <file path="else.txt" />
            </else>
            <then>
                <file path="bad.txt" />
            </then>
        </if>
    </dir>
</template>
        """
        try:
            project_root_dir = "template_xml_string__if_invalid_two_then"
            sys.stdin = io.StringIO(f"{project_root_dir}\nno_matter")
            template_generator = Temgen(TerminalUi())
            template_generator.experimental_treat_template_xml_string(template_string,
                                                                      output_dir=Path(self._output_dirpath))
            self.fail()
        except RuntimeError as ex:
            self.assertEqual(str(ex), "Too many 'then' nodes for a 'if' node.")

    def test__treat_template_xml_string__if_invalid_two_else__exception(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-z_]+" />
        <var name="if_expr" type="gstr" />
    </vars>
    <dir path="{project_root_dir}">
        <if expr="'{if_expr}' == 'yes'">
            <then>
                <file path="then.txt" />
            </then>
            <else>
                <file path="else.txt" />
            </else>
            <else>
                <file path="bad.txt" />
            </else>
        </if>
    </dir>
</template>
        """
        try:
            project_root_dir = "template_xml_string__if_invalid_two_else"
            sys.stdin = io.StringIO(f"{project_root_dir}\nno_matter")
            template_generator = Temgen(TerminalUi())
            template_generator.experimental_treat_template_xml_string(template_string,
                                                                      output_dir=Path(self._output_dirpath))
            self.fail()
        except RuntimeError as ex:
            self.assertEqual(str(ex), "Too many 'else' nodes for a 'if' node.")

    def test__treat_template_xml_string__if_invalid_missing_then__exception(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-z_]+" />
        <var name="if_expr" type="gstr" />
    </vars>
    <dir path="{project_root_dir}">
        <if expr="'{if_expr}' == 'yes'">
            <else>
                <file path="else.txt" />
            </else>
        </if>
    </dir>
</template>
        """
        try:
            project_root_dir = "template_xml_string__if_invalid_missing_then"
            sys.stdin = io.StringIO(f"{project_root_dir}\nno_matter")
            template_generator = Temgen(TerminalUi())
            template_generator.experimental_treat_template_xml_string(template_string,
                                                                      output_dir=Path(self._output_dirpath))
            self.fail()
        except RuntimeError as ex:
            self.assertEqual(str(ex), "A 'else' node is provided for a 'if' node but a 'then' node is missing.")

    def test__treat_template_xml_string__if_invalid_unknown_child__exception(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-z_]+" />
    </vars>
    <dir path="{project_root_dir}">
        <if expr="True">
            <then>
                <file path="then.txt" />
            </then>
            <file path="error.txt" />
        </if>
    </dir>
</template>
        """
        try:
            project_root_dir = "template_xml_string__if_invalid_unknown_child"
            sys.stdin = io.StringIO(f"{project_root_dir}")
            template_generator = Temgen(TerminalUi())
            template_generator.experimental_treat_template_xml_string(template_string,
                                                                      output_dir=Path(self._output_dirpath))
            self.fail()
        except RuntimeError as ex:
            self.assertEqual(str(ex), "In 'if', bad child node type: file.")


if __name__ == '__main__':
    unittest.main()
