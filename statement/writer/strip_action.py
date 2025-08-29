from enum import StrEnum


class StripAction(StrEnum):
    RAW = "raw"
    LSTRIP = "lstrip"
    RSTRIP = "rstrip"
    RSTRIP_HS = "rstrip-hs" # HS: horizontal space
    RSTRIP_NL = "rstrip-nl"
    STRIP = "strip"
    STRIP_HS = "strip-hs"
    STRIP_NL = "strip-nl"


def apply_strip(input_contents: str, strip_action: StripAction):
    match strip_action:
        case StripAction.RAW:
            return input_contents
        case StripAction.LSTRIP:
            return input_contents.lstrip()
        case StripAction.RSTRIP:
            return input_contents.rstrip()
        case StripAction.RSTRIP_HS:
            return input_contents.strip(" \t")
        case StripAction.RSTRIP_NL:
            return input_contents.rstrip() + "\n"
        case StripAction.STRIP:
            return input_contents.strip()
        case StripAction.STRIP_HS:
            return input_contents.lstrip().rstrip(" \t")
        case StripAction.STRIP_NL:
            return input_contents.strip() + "\n"
        case _:
            raise ValueError(f"'{strip_action}' is not a valid StripAction")
