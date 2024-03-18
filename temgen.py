import copy
import errno
import glob
import os
import platform
import re
import xml.etree.ElementTree as XMLTree
from pathlib import Path

import semver

import constants
import regex
from log import make_console_file_logger
from ui.abstract_ui import AbstractUi
from variables.variables_dict import VariablesDict


def environment_template_roots():
    roots = []
    temgen_templates_path = os.environ.get(f'{constants.UPPER_PROGRAM_NAME}_TEMPLATES_PATH', '')
    for path in temgen_templates_path.split(':'):
        if path:
            roots.append(Path(path))
    return roots


def linux_template_roots():
    roots = []
    home_dpath = os.environ['HOME']
    templates_dpath = Path(f"{home_dpath}/.local/share/{constants.LOWER_PROGRAM_NAME}/templates")
    templates_dpath.mkdir(parents=True, exist_ok=True)
    roots.append(templates_dpath)
    return roots


def strict_windows_template_roots():
    roots = []
    local_app_data_dpath = Path(os.environ['LOCALAPPDATA'])
    templates_dpath = local_app_data_dpath / f"{constants.LOWER_PROGRAM_NAME}/templates"
    templates_dpath.mkdir(parents=True, exist_ok=True)
    roots.append(templates_dpath)
    return roots


def windows_template_roots():
    roots = []
    roots.extend(strict_windows_template_roots())
    msystem_env_var = os.environ.get('MSYSTEM', None)
    if msystem_env_var == 'MINGW64' or msystem_env_var == 'MINGW32':
        roots.extend(linux_template_roots())
    return roots


def system_template_roots():
    platform_system = platform.system().strip().lower()
    match platform_system:
        case "windows":
            return windows_template_roots()
        case "linux":
            return linux_template_roots()
        case _:
            raise Exception(f"System not handled: '{platform_system}'")


def global_template_roots():
    roots = []
    roots.extend(system_template_roots())
    roots.extend(environment_template_roots())
    return roots


def default_template_roots():
    roots = global_template_roots()
    roots.append(Path("."))
    return roots


class Temgen:
    VERSION = semver.Version.parse('0.5.0')

    def __init__(self, ui: AbstractUi, variables=None):
        if variables is None:
            variables = VariablesDict()
        self.__ui = ui
        self.__variables = variables
        self.__template_root_dpaths = default_template_roots()
        self.__logger = make_console_file_logger(tool=constants.LOWER_PROGRAM_NAME, log_to_info=True)

    @property
    def logger(self):
        return self.__logger

    def ui(self):
        return self.__ui

    def init_variables(self):
        return self.__variables

    def template_roots(self):
        return self.__template_root_dpaths

    def find_template_file(self, template_path: Path, version_attr):
        template_dpath = template_path.parent
        template_fname = template_path.name
        has_xml_suffix = template_path.suffix == ".xml"
        rmatch = re.fullmatch(regex.TEMPLATE_FILENAME_REGEX, template_fname)
        if not rmatch:
            if not has_xml_suffix:
                raise RuntimeError(f"The path '{template_path}' is not a valid path.")
            elif template_path.exists():
                return template_path
            else:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(template_path))
        if has_xml_suffix:
            if version_attr:
                print("WARNING: The attribute version is ignored as the provided template is a file path "
                      f"(version or extension is contained in the path): '{template_path}'.")
            for template_root_dpath in self.__template_root_dpaths:
                xml_path = template_root_dpath / template_path
                if xml_path.exists():
                    return xml_path
            raise FileNotFoundError(errno.ENOENT, "Template not found", str(template_path))
        template_name = rmatch.group(regex.TEMPLATE_FILENAME_REGEX_NAME_GROUP_ID)
        template_version = rmatch.group(regex.TEMPLATE_FILENAME_REGEX_VERSION_GROUP_ID)
        if template_version:
            raise RuntimeError(f"The extension '.xml' is missing at the end of the template path: '{template_path}'.")
        if not version_attr:
            for template_root_dpath in self.__template_root_dpaths:
                xml_path = template_root_dpath / f"{template_path}.xml"
                if xml_path.exists():
                    return xml_path
            name_pattern = f"{template_name}-*.*.*.xml"
            expected_major = 0
            expected_minor = 0
            expected_patch = 0
        else:
            rmatch = re.fullmatch(regex.TRI_VERSION_REGEX, version_attr)
            if not rmatch:
                raise RuntimeError(f"Template version is not a valid version: '{version_attr}'.")
            expected_major = int(rmatch.group(regex.TRI_VERSION_REGEX_MAJOR_GROUP_ID))
            name_pattern = f"{template_name}-{expected_major}"
            expected_minor = rmatch.group(regex.TRI_VERSION_REGEX_MINOR_GROUP_ID)
            if expected_minor:
                name_pattern = f"{name_pattern}.{expected_minor}"
                expected_minor = int(expected_minor)
            else:
                name_pattern = f"{name_pattern}.*"
                expected_minor = 0
            expected_patch = rmatch.group(regex.TRI_VERSION_REGEX_PATCH_GROUP_ID)
            if expected_patch:
                name_pattern = f"{name_pattern}.{expected_patch}"
                expected_patch = int(expected_patch)
            else:
                name_pattern = f"{name_pattern}.*"
                expected_patch = 0
            name_pattern = f"{name_pattern}.xml"
        template_fpath = None
        for template_root_dpath in self.__template_root_dpaths:
            t_dir = template_root_dpath / template_dpath
            template_file_list = glob.glob(name_pattern, root_dir=t_dir)
            template_file_list.sort(reverse=True)
            template_fpath = None
            for template_file in template_file_list:
                rmatch = re.fullmatch(regex.TEMPLATE_FILENAME_REGEX, Path(template_file).name)
                if rmatch:
                    if not version_attr:
                        template_fpath = f"{t_dir}/{template_file}"
                        break
                    template_file_minor = int(rmatch.group(regex.TEMPLATE_FILENAME_REGEX_MINOR_GROUP_ID))
                    template_file_patch = int(rmatch.group(regex.TEMPLATE_FILENAME_REGEX_PATCH_GROUP_ID))
                    if template_file_minor > expected_minor \
                            or template_file_minor == expected_minor and template_file_patch >= expected_patch:
                        template_fpath = f"{t_dir}/{template_file}"
                        break
            if template_fpath is not None:
                break
        if template_fpath is None:
            raise RuntimeError(f"No template '{template_fname}' compatible with version {version_attr} found "
                               f"in {template_dpath}.")
        return Path(template_fpath)

    def treat_template_file(self, template_filepath: Path, output_dir=None):
        from statement.template_statement import TemplateStatement
        with open(template_filepath, 'r') as template_file:
            element_tree = XMLTree.parse(template_file)
        output_dir = self.__resolve_output_dir(output_dir)
        template_statement = TemplateStatement(element_tree.getroot(), None,
                                               temgen=self,
                                               template_filepath=template_filepath,
                                               variables=copy.deepcopy(self.init_variables()),
                                               output_dirpath=Path(output_dir))
        template_statement.run()

    def find_and_treat_template_file(self, template_path: Path, version: str | None = None, output_dir=None):
        template_filepath = self.find_template_file(template_path, version)
        self.treat_template_file(template_filepath, output_dir)

    def treat_template_xml_string(self, template_str: str, output_dir=None):
        from statement.template_statement import TemplateStatement
        root_element = XMLTree.fromstring(template_str)
        output_dir = self.__resolve_output_dir(output_dir)
        template_statement = TemplateStatement(root_element, None,
                                               temgen=self,
                                               variables=copy.deepcopy(self.init_variables()),
                                               output_dirpath=Path(output_dir))
        template_statement.run()

    @staticmethod
    def __resolve_output_dir(output_dir):
        if output_dir is None:
            output_dir = Path.cwd()
        if not output_dir.exists():
            raise FileNotFoundError(f"The provided output directory does not exist: '{output_dir}'.")
        return output_dir
