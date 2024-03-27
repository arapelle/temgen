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

    def test__treat_template_xml_string__base64_text_to_binary_file__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
    </vars>
    <dir path="{project_root_dir}">
        <file path="icon.png" encoding="binary" format="base64">
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACoElEQVRYR9WXgZExQRCFZyNABIgA
ESACZEAGRIAIyAARIAJEQAZkgAjcfVPVW7M7M3uzu1f3199VW9ya6X7z+nX3XKSU+nw//8yi/xJA
o9FQj8fjV1hLMDAej9Xn81HH41G9Xi9ngGq1qp7Pp+p0Oup2u5UGkQCwWCzUfD7XwdfrtVoul84A
5/NZHQ4HvaasOQGIU044Go0sugHa6/X0k7btdqvXsybErBRsNpvEPtjo9/sJugm83+9VrVZLrC2S
ngSAdrutrterBRwQzWYz1oUE4p0pxixmfGxYZYjDer1urSfvMCEGqOFwqHiPURmAJ2XyLncK2CBC
dG2eTCaKHGME4bv8jSgxQOUxiwFOgvgqlYrlB3agXQAAAsDT6VR/ksK8/cHZCbNYkPonOA8BEW7R
vuBtxbDQarUsFugNACQ4LHFqMzVsQKSyl9/x9X6/nY3LCwAnBEmDuFwuuv75rdvtxsFZPxgMtAZ8
OkC4aGW328VCzRxGOGUDgUz1U/+8R4B8EnC1WulKCLXZbKY7adA0FKGJMKMo0jRjNCRXR8wCAgPM
HSwIgOSVTSiekwLgdDppDYQaOmC/lG4mAGgl/1Ja5I8pKRNQSs9Vri5AnJo96SlrMfBTPsmdNB3p
huwBqNlBRfWiE994/3EYmafBKfTjFMXLyPY5D0lNDIBTIKgskx7ApUWMlDAjioLQABDU/X6Ple3L
ISJE8YjPtDIgNICs1gvtUC0XDBcAwAg7IbSbazQA8opj0iD1DaUy8Ux6fQB0SX33h7wW3AfEsVxG
XIHQQp67QK5GZAaUOZAGwWVESjSUidwM4Nh3dUtPxRAQhQDgmIpIX2D/LAVyMgQJ5bRjqkUEHHJy
WVOYAVOU9Hgs9H8BqwzzIP7ttaUZKAvoC4xKqRALWT+yAAAAAElFTkSuQmCC
        </file>
    </dir>
</template>
        """
        project_root_dir = "template_xml_string__base64_text_to_binary_file"
        templates_dir = config.local_templates_dirpath()
        sys.stdin = io.StringIO(f"{project_root_dir}\n{templates_dir}")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string,
                                                     output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

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
        template_generator.treat_template_xml_string(template_string,
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
        template_generator.treat_template_xml_string(template_string,
                                                     output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)

    def test__treat_template_xml_string__binary_file_copy__ok(self):
        template_string = """<?xml version="1.0"?>
<template>
    <vars>
        <var name="project_root_dir" type="gstr" regex="[a-zA-Z0-9_]+" />
    </vars>
    <dir path="{project_root_dir}">
        <file path="icon.png" encoding="binary" copy="input/data/butterfly.png" />
    </dir>
</template>
        """
        project_root_dir = "template_xml_string__binary_file_copy"
        sys.stdin = io.StringIO(f"{project_root_dir}")
        template_generator = Temgen(TerminalUi())
        template_generator.treat_template_xml_string(template_string,
                                                     output_dir=Path(self._output_dirpath))
        self._compare_output_and_expected(project_root_dir)


if __name__ == '__main__':
    unittest.main()
