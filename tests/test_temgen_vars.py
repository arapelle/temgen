import random
import unittest

from tests.test_temgen_base import TestTemgenBase


class TestTemgenVars(TestTemgenBase):
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
        input_parameters = []
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

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
        input_parameters = []
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    @staticmethod
    def vars__template_string(vars_str: str, file_contents: str):
        return f"""<?xml version="1.0"?>
<template>
    <vars>
        <var name="output_root_dir" type="gstr" />
{vars_str}
    </vars>
    <dir path="{{output_root_dir}}" >
        <file path="data.txt">
{file_contents}
        </file>
    </dir>
</template>
"""

    @staticmethod
    def vars_bool__template_string():
        vars_str = """
        <var name="first" type="bool" />
        <var name="second" type="bool" />
        <var name="third" type="bool" />
        """
        file_contents = "bools = {first}, {second}, {third}"
        return TestTemgenVars.vars__template_string(vars_str, file_contents)

    def test__treat_template_xml_string__vars_bool__y_Y_True__ok(self):
        template_string = self.vars_bool__template_string()
        project_root_dir = "template_xml_string__vars_bool__y_Y_True"
        input_parameters = ["", "false", "no", "y", "Y", "True"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_bool__n_N_False__ok(self):
        template_string = self.vars_bool__template_string()
        project_root_dir = "template_xml_string__vars_bool__n_N_False"
        input_parameters = ["", "true", "yes", "n", "N", "False"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_int__ok(self):
        vars_str = """
        <var name="first" type="int" />
        <var name="second" type="int" />
        """
        file_contents = "ints = {first}, {second}"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_int"
        input_parameters = ["7t", "42.5", "36", "-42.5", "-37"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_uint__ok(self):
        vars_str = """
        <var name="first" type="uint" />
        """
        file_contents = "uints = {first}"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_uint"
        input_parameters = ["7t", "42.5", "-42.5", "-37", "36"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_float__ok(self):
        vars_str = """
        <var name="first" type="float" />
        <var name="second" type="float" />
        <var name="third" type="float" />
        <var name="fourth" type="float" />
        <var name="fifth" type="float" />
        <var name="sixth" type="float" />
        """
        file_contents = "floats = {first}, {second}, {third}, {fourth}, {fifth}, {sixth}"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_float"
        input_parameters = ["7t", "52", "-32", "65.0", "67.2", "-72.0", "-74.3"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_str__ok(self):
        vars_str = """
        <var name="first" type="str" />
        <var name="second" type="str" />
        <var name="third" type="str" />
        <var name="fourth" type="str" />
        """
        file_contents = "strs = '{first}', '{second}', '{third}', '{fourth}'"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_str"
        input_parameters = ["", "  ", "info", "  info  "]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_pstr__ok(self):
        vars_str = """
        <var name="first" type="pstr" />
        <var name="second" type="pstr" />
        <var name="third" type="pstr" />
        """
        file_contents = "pstrs = '{first}', '{second}', '{third}'"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_pstr"
        input_parameters = ["", "  ", "info", "  info  "]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_gstr__ok(self):
        vars_str = """
        <var name="first" type="pstr" />
        <var name="second" type="pstr" />
        """
        file_contents = "gstrs = '{first}', '{second}'"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_gstr"
        input_parameters = ["", "  ", "info", "  info  "]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_bad_type__exception(self):
        var_type = "conaipa"
        vars_str = f"""
        <var name="first" type="{var_type}" />
        """
        file_contents = "any = {first}"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_gstr"
        input_parameters = ["", "  ", "info", "  info  "]
        try:
            self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)
        except RuntimeError as err:
            self.assertTrue(str(err).startswith("Bad var_type: '"))
            self.assertTrue(str(err).find(f"{var_type}") != -1)

    def test__treat_template_xml_string__vars_default__ok(self):
        vars_str = """
        <var name="first" type="gstr" default="dummy" />
        """
        file_contents = "str = '{first}'"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_default"
        input_parameters = ["\n"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__vars_regex__ok(self):
        vars_str = """
        <var name="first" type="gstr" regex="[A-Z]{4}_[0-9]{2}" />
        """
        file_contents = "str = '{first}'"
        template_string = self.vars__template_string(vars_str, file_contents)
        project_root_dir = "template_xml_string__vars_regex"
        input_parameters = ["\n", "bale_26", "BANA23", "AZER_58"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

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
        input_parameters = ["even"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

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
        input_parameters = ["super"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)


if __name__ == '__main__':
    unittest.main()
