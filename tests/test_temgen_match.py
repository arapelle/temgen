import unittest

from tests.test_temgen_base import TestTemgenBase


class TestTemgenMatch(TestTemgenBase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._local_sub_dirpath = "temgen/match"
        super().setUpClass()

    @staticmethod
    def match__template_string(default_case, no_match_file, cases=None):
        if cases is None:
            cases = """
            <case value="value">
                <file path="value.md" />
            </case>
            <case expr="[a-z]+">
                <file path="expr_az.md" />
            </case>
            <case expr="[0-9]+">
                <file path="expr_09.md" />
            </case>
            """
        return f"""<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-z09_]+" />
        <var name="expr" type="gstr" />
    </vars>
    <dir path="{{project_root_dir}}">
        <match expr="{{expr}}">
            {cases}
            {default_case}
        </match>
        {no_match_file}
    </dir>
</template>
        """

    @staticmethod
    def match_valid__template_string(with_default: bool):
        default_case = ""
        no_match_file = ""
        if with_default:
            default_case = """
            <case>
                <file path="default.md" />
            </case>
            """
        else:
            no_match_file = """
            <file path="no_match.md" />
            """
        return TestTemgenMatch.match__template_string(default_case, no_match_file)

    @staticmethod
    def match_invalid_two_default__template_string():
        default_case = """
        <case>
            <file path="default.md" />
        </case>
        """
        return TestTemgenMatch.match__template_string(default_case, "", default_case)

    @staticmethod
    def match_invalid_missing_case__template_string():
        return TestTemgenMatch.match__template_string("", "", "")

    def test__treat_template_xml_string__match_valid_value__ok(self):
        template_string = self.match_valid__template_string(with_default=True)
        project_root_dir = "template_xml_string__match_valid_value"
        input_parameters = ["value"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__match_valid_expr_09__ok(self):
        template_string = self.match_valid__template_string(with_default=True)
        project_root_dir = "template_xml_string__match_valid_expr_09"
        input_parameters = ["123"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__match_valid_default__ok(self):
        template_string = self.match_valid__template_string(with_default=True)
        project_root_dir = "template_xml_string__match_valid_default"
        input_parameters = ["az09"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__match_valid_no_match__ok(self):
        template_string = self.match_valid__template_string(with_default=False)
        project_root_dir = "template_xml_string__match_valid_no_match"
        input_parameters = ["az09"]
        self._test__treat_template_xml_string__ok(template_string, project_root_dir, input_parameters)

    def test__treat_template_xml_string__match_invalid_two_default__exception(self):
        try:
            template_string = self.match_invalid_two_default__template_string()
            project_root_dir = "template_xml_string__match_invalid_two_default"
            input_parameters = ["no_matter"]
            self._test__treat_template_xml_string__exception(template_string, project_root_dir, input_parameters)
        except RuntimeError as ex:
            self.assertEqual(str(ex), "A match node cannot have two default case nodes.")

    def test__treat_template_xml_string__match_invalid_missing_case__exception(self):
        try:
            template_string = self.match_invalid_missing_case__template_string()
            project_root_dir = "template_xml_string__match_invalid_missing_case"
            input_parameters = ["no_matter"]
            self._test__treat_template_xml_string__exception(template_string, project_root_dir, input_parameters)
        except RuntimeError as ex:
            self.assertEqual(str(ex), "case nodes are missing in match node.")


if __name__ == '__main__':
    unittest.main()
