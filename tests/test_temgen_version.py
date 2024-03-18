import io
import sys
import unittest
from pathlib import Path

import semver

from temgen import Temgen
from tests.dircmp_test_case import DirCmpTestCase
from ui.terminal_ui import TerminalUi


class TestTemgenVersion(DirCmpTestCase):
    def test__temgen_version__ok(self):
        major = 0
        minor = 5
        patch = 0
        expected_version = semver.Version(major, minor, patch)
        self.assertEqual(Temgen.VERSION.to_tuple()[0:3], expected_version.to_tuple()[0:3])

    def test__check_temgen_version__valid_version__ok(self):
        template_string = f"""<?xml version="1.0"?>
<template temgen-min-version="{Temgen.VERSION}" temgen-max-version="{Temgen.VERSION}" />
        """
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string, output_dir=Path(self._output_dirpath))

    def test__check_temgen_version__invalid_version_compared_to_min__ok(self):
        next_major_version = Temgen.VERSION.bump_major()
        template_string = f"""<?xml version="1.0"?>
<template temgen-min-version="{next_major_version}" temgen-max-version="{next_major_version}" />
        """
        template_generator = Temgen(TerminalUi())
        try:
            template_generator.treat_template_xml_string(template_string, output_dir=Path(self._output_dirpath))
        except RuntimeError as ex:
            self.assertEqual(str(ex), "temgen is not compatible with the expected min version: "
                               f"{Temgen.VERSION} (min: {next_major_version})")

    def test__check_temgen_version__invalid_version_compared_to_max__ok(self):
        template_string = f"""<?xml version="1.0"?>
<template temgen-min-version="0.0.0" temgen-max-version="0.0.0" />
        """
        template_generator = Temgen(TerminalUi())
        try:
            template_generator.treat_template_xml_string(template_string, output_dir=Path(self._output_dirpath))
        except RuntimeError as ex:
            self.assertEqual(str(ex), "temgen is not compatible with the expected max version: "
                                      f"{Temgen.VERSION} (max: 0.0.0)")

    def test__check_temgen_version__invalid_min_max_versions__ok(self):
        template_string = f"""<?xml version="1.0"?>
<template temgen-min-version="0.2.0" temgen-max-version="0.1.0" />
        """
        template_generator = Temgen(TerminalUi())
        try:
            template_generator.treat_template_xml_string(template_string, output_dir=Path(self._output_dirpath))
        except RuntimeError as ex:
            self.assertEqual(str(ex), "temgen-min-version should not be greater than temgen-max-version: "
                                      "min: 0.2.0, max: 0.1.0")


if __name__ == '__main__':
    unittest.main()
