from pathlib import Path


def local_templates_dirpath():
    return Path("input/templates")


def global_templates_dirpath():
    import temgen
    return temgen.system_template_roots()[-1]
