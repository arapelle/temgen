import io
import random
import sys
import unittest
from pathlib import Path

from ui.terminal_ui import TerminalUi
from temgen import Temgen
from tests.dircmp_test_case import DirCmpTestCase


class TestTemgenVars(DirCmpTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._local_sub_dirpath = "temgen/vars"
        super().setUpClass()

    def test__treat_template_xml_string__vars_rand_value__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="output_root_dir" type="gstr" />
        <var name="rand_i">
            <random type="int" min="45" max="100" />
        </var>
        <var name="rand_f">
            <random type="float" min="-4.1" max="12.354" />
        </var>
        <var name="rand_digit">
            <random type="digit" min-len="7" max-len="13" />
        </var>
        <var name="rand_alpha">
             <random type="alpha" min-len="4" max-len="9" />
        </var>
        <var name="rand_alpha_fixed_len">
             <random type="alpha" len="6" />
        </var>
        <var name="rand_lower">
             <random type="lower" min-len="4" max-len="9" />
        </var>
        <var name="rand_upper">
             <random type="upper" min-len="4" max-len="9" />
        </var>
        <var name="rand_alnum">
             <random type="alnum" min-len="15" max-len="26" />
        </var>
        <var name="rand_lower_sisy">
             <random type="lower_sisy" min-len="2" max-len="10" />
        </var>
        <var name="rand_upper_sisy">
             <random type="upper_sisy" min-len="2" max-len="10" />
        </var>
        <var name="rand_snake">
             <random type="snake_case" min-len="2" max-len="10" />
        </var>
        <var name="rand_format_cvqd">
             <random type="format_cvqd" fmt="Cvcvq_cvcvq_cv_dd" />
        </var>
        <var name="rand_chars">
             <random char-set="btcdaeiou" min-len="2" max-len="10" />
        </var>
    </vars>
    <dir path="{output_root_dir}" >
        <file path="data.txt" >
rand_i = {rand_i}
rand_f = {rand_f}
rand_digit = {rand_digit}
rand_alpha = {rand_alpha}
rand_alpha_fixed_len = {rand_alpha_fixed_len}
rand_lower = {rand_lower}
rand_upper = {rand_upper}
rand_alnum = {rand_alnum}
rand_lower_sisy = {rand_lower_sisy}
rand_upper_sisy = {rand_upper_sisy}
rand_snake = {rand_snake}
rand_format_cvqd = {rand_format_cvqd}
rand_chars = {rand_chars}
        </file>
    </dir>
</template>
"""
        random.seed(42)
        project_root_dir = "template_xml_string__vars_rand_value"
        sys.stdin = io.StringIO(f"{project_root_dir}")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string,
                                                     output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__vars_rand_value_default__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="output_root_dir" type="gstr" />
        <var name="rand_i">
            <random type="int" max="0" />
        </var>
        <var name="rand_f">
            <random type="float" max="0" />
        </var>
        <var name="rand_alpha">
             <random type="alpha" max-len="0" />
        </var>
    </vars>
    <dir path="{output_root_dir}" >
        <file path="data.txt" >
rand_i = {rand_i}
rand_f = {rand_f}
rand_alpha = '{rand_alpha}'
        </file>
    </dir>
</template>
"""
        random.seed(42)
        project_root_dir = "template_xml_string__vars_rand_value_default"
        sys.stdin = io.StringIO(f"{project_root_dir}")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string,
                                                     output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__vars_if__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="output_root_dir" type="gstr" />
        <var name="choice" type="gstr" />
        <if expr="'{choice}' == 'even'">
            <then>
                <var name="number" value="86420" />
            </then>
            <else>
                <var name="number" value="97531" />
            </else>
        </if>
    </vars>
    <dir path="{output_root_dir}" >
        <file path="data.txt" >
{number}
        </file>
    </dir>
</template>
"""
        random.seed(42)
        project_root_dir = "template_xml_string__vars_if"
        sys.stdin = io.StringIO(f"{project_root_dir}\neven")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string,
                                                     output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__vars_match__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="output_root_dir" type="gstr" />
        <var name="choice" type="gstr" />
        <match expr="{choice}">
            <case value="normal">
                <var name="value" value="value" />
            </case>
            <case value="super">
                <var name="value" value="super_value" />
            </case>
            <case>
                <var name="value" value="default_value" />
            </case>
        </match>
    </vars>
    <dir path="{output_root_dir}" >
        <file path="data.txt" >
{value}
        </file>
    </dir>
</template>
"""
        random.seed(42)
        project_root_dir = "template_xml_string__vars_match"
        sys.stdin = io.StringIO(f"{project_root_dir}\nsuper")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string,
                                                     output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)


if __name__ == '__main__':
    unittest.main()
