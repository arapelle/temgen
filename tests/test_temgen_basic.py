import unittest

from statement.template_statement import TemplateStatement
from tests.test_temgen_base import TestTemgenBase


class TestTemgenBasic(TestTemgenBase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        cls._expected_root_dirname = f"{os.path.dirname(os.path.abspath(__file__))}/expected"
        cls._local_sub_dirpath = "temgen/basic"
        super().setUpClass()

    def test__treat_template_xml_string__bad_root_statement_name__exception(self):
        try:
            template_string = """<?xml version="1.0"?>
<bad_name>
    <dir path="bad_dirtree">
        <file path="data.txt" />
    </dir>
</bad_name>
            """
            project_root_dir = "template_xml_string__bad_root_statement_name"
            input_parameters = []
            self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)
        except RuntimeError as err:
            self.assertEqual(str(err), f"Root node must be '{TemplateStatement.STATEMENT_LABEL}'!")

    def test__treat_template_xml_string__vars_dir_file__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
        <var name="file_name" type="gstr" regex="[a-zA-Z0-9_]+" />
        <var name="name" type="gstr" regex="[A-Z][a-z_]*" />
        <var name="color" type="gstr" regex="[a-z]+" />
    </vars>
    <dir path="{project_root_dir}">
        <file path="{file_name}.txt">
{{ 
    name = {name}, 
    color = {color}
}}
        </file>
    </dir>
</template>
        """
        project_root_dir = "template_xml_string__vars_dir_file"
        input_parameters = ["data", "Alix", "white"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__bad_format_str__exception(self):
        try:
            template_string = """<?xml version="1.0"?>
<template>
    <dir path="{whut" />
</template>
            """
            project_root_dir = "template_xml_string__bad_root_statement_name"
            input_parameters = []
            self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)
        except ValueError as err:
            self.assertEqual(str(err), "expected '}' before end of string")

    def test__treat_template_xml_string__unknown_var__exception(self):
        try:
            template_string = """<?xml version="1.0"?>
<template>
    <dir path="{unknown_var}" />
</template>
            """
            project_root_dir = "template_xml_string__bad_root_statement_name"
            input_parameters = []
            self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()
