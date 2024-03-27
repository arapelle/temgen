
def apply_strip(input_contents: str, strip_action: str):
    match strip_action:
        case "lstrip":
            return input_contents.lstrip()
        case "rstrip":
            return input_contents.rstrip()
        case "rstrip-hs":
            return input_contents.strip(" \t")
        case "rstrip-nl":
            return input_contents.rstrip() + "\n"
        case "strip":
            return input_contents.strip()
        case "strip-hs":
            return input_contents.lstrip().rstrip(" \t")
        case "strip-nl":
            return input_contents.strip() + "\n"
        case _:
            raise RuntimeError(f"Unknown strip action : {strip_action}.")
