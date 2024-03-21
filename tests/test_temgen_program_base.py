import glob
import io
import sys
from pathlib import Path

from tests.dircmp_test_case import DirCmpTestCase
from tgen import TemgenProgram


class TestTemgenProgramBase(DirCmpTestCase):
    __STDIN = sys.stdin
    __TRIVIAL_TEMPLATE_STR = """<?xml version="1.0"?>
<template>
    <vars>
{var_definitions}
    </vars>
    <dir path="{project_root_dir}" {dir_attrs}>
        <file path="data.txt" {file_attrs}>{file_contents}</file>
    </dir>
</template>
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._generated_input_dirname = getattr(cls, "_generated_input_dirname", "generated_input")
        generated_input_dir_path = Path.cwd() / f"{cls._generated_input_dirname}"
        if generated_input_dir_path.exists():
            import shutil
            shutil.rmtree(generated_input_dir_path)
        generated_input_dir_path.mkdir(exist_ok=True)
        cls._ut_context_argv = ['--terminal', '-o', f'{cls._output_dirpath}']

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.removeGeneratedInputDir()

    @classmethod
    def removeGeneratedInputDir(cls):
        cls.removeDirIfSuccess(cls._generated_input_dirname)

    def _run_generated_trivial_template_file(self, project_root_dir, argv=None, stdin_str=None, **kargs):
        if argv is None:
            argv = []
        generated_template_file_path = self._generate_trivial_template_file(project_root_dir, **kargs)
        temgen = TemgenProgram(self._ut_context_argv + argv + ['--', generated_template_file_path])
        if stdin_str:
            sys.stdin = io.StringIO(stdin_str)
        else:
            sys.stdin = TestTemgenProgramBase.__STDIN
        temgen.run()
        return self._extract_files_contents(project_root_dir)

    def _extract_files_contents(self, project_root_dir):
        root_dir = f"{self._output_dirpath}/{project_root_dir}"
        file_list = glob.glob("**/*.txt", root_dir=root_dir, recursive=True)
        file_contents_dict = {}
        for txt_file in file_list:
            with open(f"{root_dir}/{txt_file}") as data_file:
                file_contents_dict[Path(txt_file).as_posix()] = data_file.read()
        return file_contents_dict

    def _test_generated_trivial_template_file(self, project_root_dir, argv=None, stdin_str=None, **kargs):
        if argv is None:
            argv = []
        self._generate_trivial_template_file(project_root_dir, **kargs)
        self._test_generated_template_file(project_root_dir, argv, stdin_str)

    def _test_generated_template_file(self, project_root_dir, argv=None, stdin_str=None):
        if argv is None:
            argv = []
        generated_input_dir_path = Path(f"{self._generated_input_dirname}")
        generated_template_file_path = f'{generated_input_dir_path}/{project_root_dir}.xml'
        temgen = TemgenProgram(self._ut_context_argv + argv + ['--', generated_template_file_path])
        if stdin_str:
            sys.stdin = io.StringIO(stdin_str)
        else:
            sys.stdin = TestTemgenProgramBase.__STDIN
        temgen.run()
        self._compare_output_and_expected(project_root_dir)

    def _generate_trivial_template_file(self, project_root_dir, **kargs):
        keys = ["var_definitions", "dir_attrs", "file_attrs", "file_contents"]
        for key in keys:
            if key not in kargs:
                kargs[key] = ""
        generated_input_dir_path = Path(f"{self._generated_input_dirname}")
        generated_template_file_path = f'{generated_input_dir_path}/{project_root_dir}.xml'
        with open(generated_template_file_path, 'w') as generated_template_file:
            template_contents = self.__TRIVIAL_TEMPLATE_STR.format(project_root_dir=project_root_dir, **kargs)
            generated_template_file.write(template_contents)
        return generated_template_file_path

    def _run_template_file(self, template_filestem, argv=None, stdin_str=None, context_argv=None):
        if argv is None:
            argv = ['--', f'input/{template_filestem}.xml']
        if context_argv is None:
            context_argv = self._ut_context_argv
        temgen = TemgenProgram(context_argv + argv)
        if stdin_str:
            sys.stdin = io.StringIO(stdin_str)
        else:
            sys.stdin = TestTemgenProgramBase.__STDIN
        temgen.run()

    def _test_template_file(self, template_filestem, project_root_dir=None, argv=None, stdin_str=None,
                            context_argv=None):
        if project_root_dir is None:
            project_root_dir = template_filestem
        self._run_template_file(template_filestem, argv, stdin_str, context_argv)
        self._compare_output_and_expected(project_root_dir)

    def _run_template_path_template_versoin(self, template_path, template_version, argv=None, stdin_str=None,
                                            context_argv=None):
        if argv is None:
            argv = ['--', template_path, template_version]
        if context_argv is None:
            context_argv = self._ut_context_argv
        temgen = TemgenProgram(context_argv + argv)
        if stdin_str:
            sys.stdin = io.StringIO(stdin_str)
        else:
            sys.stdin = TestTemgenProgramBase.__STDIN
        temgen.run()

    def _test_template_path_template_version(self, template_path, template_version, project_root_dir,
                                             argv=None, stdin_str=None, context_argv=None):
        self._run_template_path_template_versoin(template_path, template_version, argv, stdin_str, context_argv)
        self._compare_output_and_expected(project_root_dir)
