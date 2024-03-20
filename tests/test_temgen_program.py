import datetime
import random
import shutil
import sys
import unittest
from json import JSONDecodeError
from pathlib import Path

import temgen
from statement.template_statement import TemplateStatement
from variables.variables_dict import VariablesDict
from tests.test_temgen_program_base import TestTemgenProgramBase


class TestTemgenProgram(TestTemgenProgramBase):
    def test__bad_dirtree__bad_root_node_name__err(self):
        try:
            self._test_template_file("bad_root_node_name")
            self.fail()
        except RuntimeError as err:
            self.assertEqual(str(err), f"Root node must be '{TemplateStatement.STATEMENT_LABEL}'!")

    def test__simple_dirtree__valid__ok(self):
        self._test_template_file("simple_dirtree")

    def test__simple_dirtree__template_not_found__err(self):
        template_fpath = "template_not_found"
        try:
            self._run_template_file(template_fpath)
            self.fail()
        except FileNotFoundError as err:
            self.assertTrue(str(err).find(f"Template not found") != -1)
            self.assertTrue(str(err).find(template_fpath) != -1)

    def test__simple_dirtree__file_not_found__err(self):
        template_fpath = "template__not__found"
        try:
            self._run_template_file(template_fpath)
            self.fail()
        except FileNotFoundError as err:
            err_str = str(err)
            self.assertTrue(err_str.find(f"Template not found") == -1)
            self.assertTrue(err_str.find(template_fpath) != -1)

    def test__simple_fdirtree__valid__ok(self):
        self._test_template_file("simple_fdirtree", stdin_str='arba\ncore')

    def test__match_fdirtree__valid_value__ok(self):
        output_root_dir = "match_valid_value"
        in_str = f'{output_root_dir}\nvalue'
        self._test_template_file("match_fdirtree__valid_with_default",
                                 project_root_dir=output_root_dir, stdin_str=in_str)

    def test__match_fdirtree__valid_expr_09__ok(self):
        output_root_dir = "match_valid_expr_09"
        in_str = f'{output_root_dir}\n1235'
        self._test_template_file("match_fdirtree__valid_with_default",
                                 project_root_dir=output_root_dir, stdin_str=in_str)

    def test__match_fdirtree__valid_default__ok(self):
        output_root_dir = "match_valid_default"
        in_str = f'{output_root_dir}\ndefault_case'
        self._test_template_file("match_fdirtree__valid_with_default",
                                 project_root_dir=output_root_dir, stdin_str=in_str)

    def test__match_fdirtree__valid_no_match__ok(self):
        output_root_dir = "match_valid_no_match"
        in_str = f'{output_root_dir}\nno_match'
        self._test_template_file("match_fdirtree__valid_without_default",
                                 project_root_dir=output_root_dir, stdin_str=in_str)

    def test__match_fdirtree__invalid_two_default__exception(self):
        try:
            output_root_dir = "match_fdirtree__invalid_two_default"
            in_str = f'{output_root_dir}\nno_match'
            self._test_template_file(output_root_dir, stdin_str=in_str)
            self.fail()
        except Exception as ex:
            self.assertEqual(str(ex), "A match node cannot have two default case nodes.")

    def test__match_fdirtree__invalid_missing_case__exception(self):
        try:
            output_root_dir = "match_fdirtree__invalid_missing_case"
            in_str = f'{output_root_dir}\nno_match'
            self._test_template_file(output_root_dir, stdin_str=in_str)
            self.fail()
        except Exception as ex:
            self.assertEqual(str(ex), "case nodes are missing in match node.")

    def test__cli_args__invalid_output_dir__exception(self):
        try:
            context_argv = ['--terminal', '-o', f'__not_found__']
            output_root_dir = "cli_args__invalid_output_dir"
            in_str = f'{output_root_dir}\nok\nok'
            self._test_template_file("simple_fdirtree", project_root_dir=output_root_dir, stdin_str=in_str,
                                     context_argv=context_argv)
            self.fail()
        except Exception as ex:
            self.assertEqual(str(ex), "The provided output directory does not exist: '__not_found__'.")

    def test__cli_args__valid_v__ok(self):
        output_root_dir = "cli_args__valid_v"
        args = ['--var', 'text=coucou', 'other_text=']
        var_defs = '<var name="text" />\n<var name="other_text" />'
        self._test_generated_trivial_template_file(output_root_dir, argv=args,
                                                   var_definitions=var_defs, file_contents=":{text}:{other_text}:")

    def test__cli_args__valid_var__ok(self):
        output_root_dir = "cli_args__valid_var"
        args = ['--var', 'text=coucou', 'other_text=']
        var_defs = '<var name="text" />\n<var name="other_text" />'
        self._test_generated_trivial_template_file(output_root_dir, argv=args,
                                                   var_definitions=var_defs, file_contents=":{text}:{other_text}:")

    def test__cli_args__valid_var_override__ok(self):
        output_root_dir = "cli_args__valid_var_override"
        args = ['--var', 'text=good_value', 'other_text=']
        var_defs = '<var name="text" value="bad_value" />\n<var name="other_text" />'
        self._test_generated_trivial_template_file(output_root_dir, argv=args,
                                                   var_definitions=var_defs, file_contents=":{text}:{other_text}:")

    def test__cli_args__invalid_v__exception(self):
        bad_var = 'bad-var=coucou'
        try:
            output_root_dir = "cli_args__invalid_v"
            args = ['-v', 'text=coucou', bad_var]
            var_defs = '<var name="text" value="{text}" />'
            self._run_generated_trivial_template_file(output_root_dir, argv=args,
                                                      var_definitions=var_defs, file_contents="{text}")
            self.fail()
        except RuntimeError as err:
            self.assertEqual(str(err), bad_var)

    def test__trivial_template__bad_format_str__exception(self):
        try:
            self._run_generated_trivial_template_file("bad_format_str", file_contents="{whut")
            self.fail()
        except ValueError as err:
            self.assertEqual(str(err), "expected '}' before end of string")

    def test__trivial_template__unknown_var__exception(self):
        try:
            self._run_generated_trivial_template_file("unknown_var", file_contents="{unknown_var}")
            self.fail()
        except KeyError:
            pass

    def test__var_file__valid_var_file__ok(self):
        output_root_dir = "var_file__valid_var_file"
        args = ['--var-file', 'input/var_files/texts.json']
        var_defs = '<var name="text" />\n<var name="other_text" />'
        self._test_generated_trivial_template_file(output_root_dir, argv=args,
                                                   var_definitions=var_defs, file_contents=":{text}:{other_text}:")

    def test__var_file__unknown_var_file__exception(self):
        json_fpath = 'input/var_files/not_found.json'
        try:
            output_root_dir = "var_file__unknown_var_file"
            args = ['--var-file', json_fpath]
            self._run_generated_trivial_template_file(output_root_dir, argv=args)
            self.fail()
        except FileNotFoundError as err:
            self.assertTrue(str(err).find(f"No such file or directory: '{json_fpath}'") != -1)

    def test__var_file__bad_var_file__exception(self):
        json_fpath = 'input/var_files/bad.json'
        try:
            output_root_dir = "var_file__bad_var_file"
            args = ['--var-file', json_fpath]
            var_defs = '<var name="text" />\n<var name="other_text" />'
            self._run_generated_trivial_template_file(output_root_dir, argv=args,
                                                      var_definitions=var_defs, file_contents=":{text}:{other_text}:")
            self.fail()
        except JSONDecodeError:
            pass

    def test__custom_ui__valid_cmd__ok(self):
        output_root_dir = "custom_ui__valid_cmd"
        args = ['-C', f'{sys.executable} input/custom_ui/myui.py']
        var_defs = '<var name="text" value="good_value" />\n<var name="other_text" value="" />'
        self._test_generated_trivial_template_file(output_root_dir, argv=args,
                                                   var_definitions=var_defs, file_contents=":{text}:{other_text}:")

    def test__custom_ui__invalid_cmd__exception(self):
        try:
            output_root_dir = "custom_ui__invalid_cmd"
            args = ['-C', f'{sys.executable} input/custom_ui/not_found.py']
            var_defs = '<var name="text" value="good_value" />\n<var name="other_text" value="" />'
            self._run_generated_trivial_template_file(output_root_dir, argv=args,
                                                      var_definitions=var_defs, file_contents=":{text}:{other_text}:")
        except RuntimeError as err:
            self.assertTrue(str(err).find("Execution of custom ui did not work well") != -1)

    def test__file_fdirtree__format_raw__ok(self):
        output_root_dir = "file_fdirtree__format_raw"
        in_str = f'{output_root_dir}\nraw\nunused_message'
        self._test_template_file("file_fdirtree__valid_format", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_fdirtree__copy_raw__ok(self):
        output_root_dir = "file_fdirtree__copy_raw"
        in_str = f'{output_root_dir}\nfruits.txt\nraw\nPeer'
        self._test_template_file("file_fdirtree__copy", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_fdirtree__copy_format__ok(self):
        output_root_dir = "file_fdirtree__copy_format"
        in_str = f'{output_root_dir}\nfruits.txt\nformat\nPear'
        self._test_template_file("file_fdirtree__copy", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_fdirtree__copy_bad_file__exception(self):
        filename = "unknown.txt"
        try:
            output_root_dir = "file_fdirtree__copy_bad_file"
            in_str = f'{output_root_dir}\n{filename}\nformat\nPear'
            self._test_template_file("file_fdirtree__copy", project_root_dir=output_root_dir, stdin_str=in_str)
            self.fail()
        except FileNotFoundError as err:
            self.assertTrue(str(err).find(f"{filename}") != -1)

    def test__trivial_fdirtree__builtin_CURRENT_TEMPLATE_DIR__ok(self):
        project_root_dir = f"builtin_{VariablesDict.TEMPLATE_DIR_VARNAME[1:]}"
        f_contents = f"{{{VariablesDict.TEMPLATE_DIR_VARNAME}}}"
        file_contents_dict = self._run_generated_trivial_template_file(project_root_dir, file_contents=f_contents)
        extracted_value = file_contents_dict["data.txt"]
        extracted_value = Path(extracted_value).resolve()
        expected_value = (Path.cwd() / self._generated_input_dirname).resolve()
        self.assertEqual(extracted_value, expected_value)

    def test__trivial_fdirtree__builtin_date_vars__ok(self):
        project_root_dir = "builtin_date_vars"
        f_contents = "{$YEAR},{$MONTH},{$DAY},{$DATE_YMD},{$DATE_Y_M_D}"
        file_contents_dict = self._run_generated_trivial_template_file(project_root_dir, file_contents=f_contents)
        extracted_value = file_contents_dict["data.txt"]
        expected_value = datetime.date.today().strftime("%Y,%m,%d,%Y%m%d,%Y-%m-%d")
        self.assertEqual(extracted_value, expected_value)

    @classmethod
    def setUpClass(cls) -> None:
        cls._local_sub_dirpath = "temgen_program"
        super().setUpClass()
        template_local_root = "temfile"
        template_root = Path(f"{temgen.system_template_roots()[-1]}/{template_local_root}")
        template_root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile("input/templates/temfile-1.0.0.xml", f"{template_root}/temfile-1.0.0.xml")
        shutil.copyfile("input/templates/temfile-1.1.0.xml", f"{template_root}/temfile-1.1.0.xml")
        shutil.copyfile("input/templates/temfile-1.1.1.xml", f"{template_root}/temfile-1.1.1.xml")
        shutil.copyfile("input/templates/temfile-1.2.0.xml", f"{template_root}/temfile-1.2.0.xml")
        shutil.copyfile("input/templates/temfile-2.0.0.xml", f"{template_root}/temfile-2.0.0.xml")
        template_local_root = "temdir"
        template_root = Path(f"{temgen.system_template_roots()[-1]}/{template_local_root}")
        template_root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile("input/templates/temdir-1.0.0.xml", f"{template_root}/temdir-1.0.0.xml")
        shutil.copyfile("input/templates/temdir-1.1.0.xml", f"{template_root}/temdir-1.1.0.xml")
        shutil.copyfile("input/templates/temdir.xml", f"{template_root}/temdir.xml")

    def test__dir_template__local_xml__ok(self):
        output_root_dir = "dir_template__valid_local_xml"
        in_str = f'{output_root_dir}\ninput/templates\ntemdir-1.0.0.xml\nmy_equipment'
        self._test_template_file("dir_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__dir_template__global_xml__ok(self):
        output_root_dir = "dir_template__valid_global_xml"
        in_str = f'{output_root_dir}\ntemdir\ntemdir-1.0.0.xml\nmy_equipment'
        self._test_template_file("dir_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__local_xml__ok(self):
        output_root_dir = "file_template__valid_local_xml"
        in_str = f'{output_root_dir}\ninput/templates\ntemfile-1.0.0.xml\nobject.txt\nsword'
        self._test_template_file("file_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__local_xml_ver__warning(self):
        output_root_dir = "file_template__valid_local_xml_ver"
        in_str = f'{output_root_dir}\ninput/templates\ntemfile-1.0.0.xml\n1.0.0\nobject.txt\nsword'
        self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__global_xml__ok(self):
        output_root_dir = "file_template__valid_global_xml"
        in_str = f'{output_root_dir}\ntemfile\ntemfile-1.0.0.xml\nobject.txt\nsword'
        self._test_template_file("file_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__local_path_1_1_0__ok(self):
        output_root_dir = "file_template__valid_local_path_1_1_0"
        in_str = f'{output_root_dir}\ninput/templates\ntemfile\n1.1.0\nobject.txt\nsword'
        self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__local_path_1_1__ok(self):
        output_root_dir = "file_template__valid_local_path_1_1"
        in_str = f'{output_root_dir}\ninput/templates\ntemfile\n1.1\nobject.txt\nsword'
        self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__local_path_1__ok(self):
        output_root_dir = "file_template__valid_local_path_1"
        in_str = f'{output_root_dir}\ninput/templates\ntemfile\n1\nobject.txt\nsword'
        self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__global_path_1_1_0__ok(self):
        output_root_dir = "file_template__valid_global_path_1_1_0"
        in_str = f'{output_root_dir}\ntemfile\ntemfile\n1.1.0\nobject.txt\nsword'
        self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__global_path_1_1__ok(self):
        output_root_dir = "file_template__valid_global_path_1_1"
        in_str = f'{output_root_dir}\ntemfile\ntemfile\n1.1\nobject.txt\nsword'
        self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__global_path_1__ok(self):
        output_root_dir = "file_template__valid_global_path_1"
        in_str = f'{output_root_dir}\ntemfile\ntemfile\n1\nobject.txt\nsword'
        self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__local_path_4_0_4__err(self):
        filename = "temfile"
        try:
            output_root_dir = "file_template__invalid_local_path_4_0_4"
            in_str = f'{output_root_dir}\ninput/templates\n{filename}\n4.0.4\nobject.txt\nsword'
            self._test_template_file("file_template__valid_ver", project_root_dir=output_root_dir, stdin_str=in_str)
        except RuntimeError as err:
            self.assertTrue(str(err).startswith("No template "))
            self.assertTrue(str(err).find(f"compatible with version ") != -1)
            self.assertTrue(str(err).find(f"{filename}") != -1)

    def test__file_template__local_path_last__ok(self):
        output_root_dir = "file_template__valid_local_path_last"
        in_str = f'{output_root_dir}\ninput/templates\ntemfile\nobject.txt\nsword\nshield'
        self._test_template_file("file_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__file_template__global_path_last__ok(self):
        output_root_dir = "file_template__valid_global_path_last"
        in_str = f'{output_root_dir}\ntemfile\ntemfile\nobject.txt\nsword\nshield'
        self._test_template_file("file_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__dir_template__local_path_xml__ok(self):
        output_root_dir = "dir_template__valid_local_path_xml"
        in_str = f'{output_root_dir}\ninput/templates\ntemdir\nmy_equipment'
        self._test_template_file("dir_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__dir_template__global_path_xml__ok(self):
        output_root_dir = "dir_template__valid_global_path_xml"
        in_str = f'{output_root_dir}\ntemdir\ntemdir\nmy_equipment'
        self._test_template_file("dir_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__dir_template__invalid_path_ver_wo_ext__err(self):
        filename = "temdir-1.0.0"
        try:
            output_root_dir = "dir_template__invalid_local_path_xml"
            in_str = f'{output_root_dir}\ninput/templates\n{filename}\nmy_equipment'
            self._test_template_file("dir_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)
            self.fail()
        except RuntimeError as err:
            self.assertTrue(str(err).startswith("The extension '.xml' is missing at the end of the template path: "))
            self.assertTrue(str(err).find(f"{filename}") != -1)

    def test__dir_template__invalid_xml__err(self):
        filename = "notfound.xml"
        try:
            output_root_dir = "dir_template__invalid_xml"
            in_str = f'{output_root_dir}\ninput/templates\n{filename}\nmy_equipment'
            self._test_template_file("dir_template__valid", project_root_dir=output_root_dir, stdin_str=in_str)
            self.fail()
        except FileNotFoundError as err:
            self.assertTrue(str(err).find("Template not found: "))
            self.assertTrue(str(err).find(f"{filename}") != -1)

    def test__vars_bool__y_Y_True__ok(self):
        output_root_dir = "vars_bool__y_Y_True"
        var_defs = '<var name="first" type="bool" />'
        var_defs += '<var name="second" type="bool" />'
        var_defs += '<var name="third" type="bool" />'
        in_str = "f\nfalse\nno\ny\nY\nTrue"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="{first}\n{second}\n{third}\n")

    def test__vars_bool__n_N_False__ok(self):
        output_root_dir = "vars_bool__n_N_False"
        var_defs = '<var name="first" type="bool" />'
        var_defs += '<var name="second" type="bool" />'
        var_defs += '<var name="third" type="bool" />'
        in_str = "t\ntrue\nyes\nn\nN\nFalse"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="{first}\n{second}\n{third}\n")

    def test__vars_int__ints__ok(self):
        output_root_dir = "vars_int__ints"
        var_defs = '<var name="first" type="int" />'
        var_defs += '<var name="second" type="int" />'
        in_str = "7t\n42.5\n36\n-42.5\n-37"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="{first}\n{second}\n")

    def test__vars_uint__uint__ok(self):
        output_root_dir = "vars_uint__uint"
        var_defs = '<var name="first" type="uint" />'
        in_str = "7t\n42.5\n-42.5\n-37\n36"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="{first}\n")

    def test__vars_float__ints_floats__ok(self):
        output_root_dir = "vars_float__ints_floats"
        var_defs = '<var name="first" type="float" />'
        var_defs += '<var name="second" type="float" />'
        var_defs += '<var name="third" type="float" />'
        var_defs += '<var name="fourth" type="float" />'
        var_defs += '<var name="fifth" type="float" />'
        var_defs += '<var name="sixth" type="float" />'
        in_str = "7t\n52\n-32\n65.0\n67.2\n-72.0\n-74.3"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="{first}\n{second}\n{third}\n{fourth}\n{fifth}\n"
                                                               "{sixth}\n")

    def test__vars_str__strs__ok(self):
        output_root_dir = "vars_str__strs"
        var_defs = '<var name="first" type="str" />'
        var_defs += '<var name="second" type="str" />'
        var_defs += '<var name="third" type="str" />'
        var_defs += '<var name="fourth" type="str" />'
        in_str = "\n  \ninfo\n  info  \n"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="'{first}'\n'{second}'\n'{third}'\n'{fourth}'\n")

    def test__vars_pstr__pstrs__ok(self):
        output_root_dir = "vars_pstr__pstrs"
        var_defs = '<var name="first" type="pstr" />'
        var_defs += '<var name="second" type="pstr" />'
        var_defs += '<var name="third" type="pstr" />'
        in_str = "\n  \ninfo\n  info  \n"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="'{first}'\n'{second}'\n'{third}'\n")

    def test__vars_gstr__gstrs__ok(self):
        output_root_dir = "vars_gstr__gstrs"
        var_defs = '<var name="first" type="gstr" />'
        var_defs += '<var name="second" type="gstr" />'
        in_str = "\n  \ninfo\n  info  \n"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="'{first}'\n'{second}'\n")

    def test__vars_invalid_type__invalid__err(self):
        var_type = "conaipa"
        try:
            output_root_dir = "vars_invalid_type__invalid"
            var_defs = f'<var name="first" type="{var_type}" />'
            in_str = "\n  \ninfo\n  info  \n"
            self._run_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                      file_contents="{first}\n")
        except RuntimeError as err:
            self.assertTrue(str(err).startswith("Bad var_type: '"))
            self.assertTrue(str(err).find(f"{var_type}") != -1)

    def test__vars_default__empty_str__ok(self):
        output_root_dir = "vars_default__empty_str"
        var_defs = '<var name="first" type="gstr" default="dummy" />'
        in_str = "\n"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="'{first}'\n")

    def test__vars_regex__bad_str_good_str__ok(self):
        output_root_dir = "vars_regex__bad_str_good_str"
        var_defs = '<var name="first" type="gstr" regex="[A-Z]{4}_[0-9]{2}" />'
        in_str = "\nbale_26\nBANA23\nAZER_58"
        self._test_generated_trivial_template_file(output_root_dir, stdin_str=in_str, var_definitions=var_defs,
                                                   file_contents="'{first}'\n")

    def test__vars_rand_value__all__ok(self):
        random.seed(42)
        output_root_dir = "vars_rand_value__all"
        in_str = f"{output_root_dir}"
        self._test_template_file("vars_rand_value", project_root_dir=output_root_dir, stdin_str=in_str)

    def test__builtins__template__ok(self):
        project_root_dir = "builtins__template"
        in_str = f"input/templates/template_builtins.xml\n{project_root_dir}"
        self._run_template_file("dir_template__builtins", stdin_str=in_str)
        file_contents_dict = self._extract_files_contents(project_root_dir)
        template_data = file_contents_dict["subdir/template_data.txt"].strip().split()
        caller_data = file_contents_dict["caller_data.txt"].strip().split()
        cwd = Path.cwd()
        self.assertEqual(Path(template_data[0]).as_posix(), Path(f"{cwd}/input/templates").as_posix())
        self.assertEqual(Path(caller_data[0]).as_posix(), Path(f"{cwd}/input").as_posix())
        self.assertEqual(caller_data[1], project_root_dir)

    def test__template_path_and_version__temdir_1__ok(self):
        project_root_dir = "local__temdir__1"
        in_str = f"{project_root_dir}"
        self._test_template_path_template_version(f"input/templates/temdir", "1", project_root_dir, stdin_str=in_str)

    def test__template_path_and_version__temdir_1_0__ok(self):
        project_root_dir = "local__temdir__1_0"
        in_str = f"{project_root_dir}"
        self._test_template_path_template_version(f"input/templates/temdir", "1.0", project_root_dir, stdin_str=in_str)

    def test__template_path_and_version__global_temdir_1__ok(self):
        project_root_dir = "global__temdir__1"
        in_str = f"{project_root_dir}"
        self._test_template_path_template_version(f"temdir/temdir", "1", project_root_dir, stdin_str=in_str)

    def test__template_path_and_version__global_temdir_1_0__ok(self):
        project_root_dir = "global__temdir__1_0"
        in_str = f"{project_root_dir}"
        self._test_template_path_template_version(f"temdir/temdir", "1.0", project_root_dir, stdin_str=in_str)


if __name__ == '__main__':
    unittest.main()
