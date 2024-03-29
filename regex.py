import re


# classic_name (like hello_world_01)
CLASSIC_NAME_RESTR = r'[a-zA-Z][a-zA-Z0-9]*(_[a-zA-Z0-9]+)*'

# tri_version (like 0.1.0)
TRI_VERSION_RESTR = r'(0|[1-9]\d*)(\.(0|[1-9]\d*))?(\.(0|[1-9]\d*))?'
TRI_VERSION_REGEX = re.compile(TRI_VERSION_RESTR)
TRI_VERSION_REGEX_MAJOR_GROUP_ID = 1
TRI_VERSION_REGEX_MINOR_GROUP_ID = 3
TRI_VERSION_REGEX_PATCH_GROUP_ID = 5

# full_tri_version (like 0.1.0, or 0.1 or 0)
FULL_TRI_VERSION_RESTR = r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
FULL_TRI_VERSION_REGEX = re.compile(FULL_TRI_VERSION_RESTR)
FULL_TRI_VERSION_REGEX_MAJOR_GROUP_ID = 1
FULL_TRI_VERSION_REGEX_MINOR_GROUP_ID = 2
FULL_TRI_VERSION_REGEX_PATCH_GROUP_ID = 3

# template_filename := (classic_name)-(tri_version)\.xml
TEMPLATE_FILENAME_RESTR = f"({CLASSIC_NAME_RESTR})(-({FULL_TRI_VERSION_RESTR}))?(\.xml)?"
TEMPLATE_FILENAME_REGEX = re.compile(f"({CLASSIC_NAME_RESTR})(-({FULL_TRI_VERSION_RESTR}))?(\.xml)?")
TEMPLATE_FILENAME_REGEX_NAME_GROUP_ID = 1
TEMPLATE_FILENAME_REGEX_VERSION_GROUP_ID = 3
TEMPLATE_FILENAME_REGEX_MAJOR_GROUP_ID = 5
TEMPLATE_FILENAME_REGEX_MINOR_GROUP_ID = 6
TEMPLATE_FILENAME_REGEX_PATCH_GROUP_ID = 7
TEMPLATE_FILENAME_REGEX_EXT_GROUP_ID = 8
# namespace_path := namespace_name(/+namespace_name)*/*
NAMESPACE_NAME_RESTR = CLASSIC_NAME_RESTR
NAMESPACE_PATH_RESTR = fr"({NAMESPACE_NAME_RESTR})(/+{NAMESPACE_NAME_RESTR})*/*"
# template_path := (namespace_path/)?template_name
TEMPLATE_PATH_REGEX = re.compile(f"({NAMESPACE_PATH_RESTR}/)?({TEMPLATE_FILENAME_RESTR})")
TEMPLATE_PATH_REGEX_DIR_GROUP_ID = 1
TEMPLATE_PATH_REGEX_FILENAME_GROUP_ID = 6
TEMPLATE_PATH_REGEX_NAME_GROUP_ID = 7
TEMPLATE_PATH_REGEX_VERSION_GROUP_ID = 10
TEMPLATE_PATH_REGEX_MAJOR_GROUP_ID = 11
TEMPLATE_PATH_REGEX_MINOR_GROUP_ID = 12
TEMPLATE_PATH_REGEX_PATCH_GROUP_ID = 13

VAR_NAME_REGEX = re.compile(r'\A[a-zA-Z][a-zA-Z0-9_]*\Z')
VAR_REGEX = re.compile(r"\{([a-zA-Z][a-zA-Z0-9_]*)\}|(\{\{|\}\})")
VAR_NAME_GROUP_ID = 1
SKIP_GROUP_ID = VAR_NAME_GROUP_ID + 1
