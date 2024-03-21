import filecmp
import os
import shutil
from pathlib import Path
from unittest import TestCase


class DirCmpTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._expected_root_dirname = getattr(cls, "_expected_root_dirname", "expected")
        cls._output_root_dirname = getattr(cls, "_output_root_dirname", "output")
        cls._local_sub_dirpath = getattr(cls, "_local_sub_dirpath", "")
        cls._output_dirpath = f"{cls._output_root_dirname}/{cls._local_sub_dirpath}"
        cls._expected_dirpath = f"{cls._expected_root_dirname}/{cls._local_sub_dirpath}"
        output_dpath = Path(cls._output_dirpath)
        if output_dpath.exists():
            shutil.rmtree(output_dpath)
        output_dpath.mkdir(parents=True)

    @classmethod
    def executionIsSuccess(cls):
        return len(cls._unit_tests_result.errors) == 0 and len(cls._unit_tests_result.failures) == 0

    @classmethod
    def tearDownClass(cls):
        cls.removeOutputDir()

    @classmethod
    def removeOutputDir(cls):
        if cls.executionIsSuccess():
            assert str(cls._output_dirpath).find(cls._output_root_dirname) != -1
            opath = Path(cls._output_dirpath).absolute().parent
            orpath = Path(cls._output_root_dirname).absolute()
            shutil.rmtree(Path(cls._output_dirpath))
            while opath != orpath and len(os.listdir(opath)) == 0:
                shutil.rmtree(opath)
                opath = opath.parent
            if orpath.exists() and len(os.listdir(orpath)) == 0:
                shutil.rmtree(orpath)

    @classmethod
    def removeDirIfSuccess(cls, dir_path):
        if cls.executionIsSuccess():
            shutil.rmtree(Path(dir_path))

    @classmethod
    def __set_unit_tests_result(cls, unit_tests_result):
        cls._unit_tests_result = unit_tests_result

    def run(self, result=None):
        assert result is not None
        self.__set_unit_tests_result(result)
        TestCase.run(self, result)  # call superclass run method

    def _compare_output_and_expected(self, dir_name):
        left_dir = f"{self._output_dirpath}/{dir_name}"
        right_dir = f"{self._expected_dirpath}/{dir_name}"
        self._compare_directories(filecmp.dircmp(left_dir, right_dir))

    def _compare_directories(self, dcmp):
        if dcmp.diff_files:
            for diff_file in dcmp.diff_files:
                left_path = f"{dcmp.left}/{diff_file}"
                right_path = f"{dcmp.right}/{diff_file}"
                self._diff_files(left_path, right_path)
        if dcmp.common_funny:
            common_funny = [f"{dcmp.right}/{x}" for x in dcmp.common_funny]
            self.assertListEqual([], common_funny)
        if dcmp.funny_files:
            funny_files = [f"{dcmp.right}/{x}" for x in dcmp.funny_files]
            self.assertListEqual([], funny_files)
        if dcmp.right_only:
            right_only = [f"{dcmp.right}/{x}" for x in dcmp.right_only]
            self.assertListEqual([], right_only)
        if dcmp.left_only:
            left_only = [f"{dcmp.left}/{x}" for x in dcmp.left_only]
            self.assertListEqual([], left_only)
        # recurse:
        for sub_dcmp in dcmp.subdirs.values():
            self._compare_directories(sub_dcmp)

    def _diff_files(self, left_path, right_path):
        print("### start of _diff_files ###")
        import difflib
        with open(left_path) as left_file:
            left_text = left_file.readlines()
        with open(right_path) as right_file:
            right_text = right_file.readlines()
        # Find and print the diff:
        for line in difflib.unified_diff(left_text, right_text,
                                         fromfile=left_path, tofile=right_path):
            print(line.rstrip())
            if line.startswith('---') or line.startswith('+++') or line.startswith(' '):
                continue
            assert len(line) > 0
            if line[0] == '+':
                self.fail(f"Difference met while comparing:\n  '{left_path}' and\n  '{right_path}'.")
        self.fail(f"Difference met while comparing:\n  '{left_path}' and\n  '{right_path}'.")
