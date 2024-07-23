import re
from argparse import ArgumentParser


class CliCommand:
    def __init__(self, parent, command_name=None, **kwargs):
        self.__parent = parent
        self.__command_name = command_name if command_name is not None else self.__default_command_name()
        self.__subcommand_name = f"{self.command_name().replace('-', '_')}_subcommand"
        subparsers = kwargs.get("subparsers")
        if subparsers is None:
            assert "subparsers" not in kwargs
            self.__arg_parser: ArgumentParser = ArgumentParser(self.command_name(), **kwargs)
        else:
            del kwargs["subparsers"]
            help_message = kwargs.pop("help", "")
            self.__arg_parser: ArgumentParser = subparsers.add_parser(self.command_name(),
                                                                      help=help_message,
                                                                      **kwargs)

    def arg_parser(self):
        return self.__arg_parser

    def command_name(self):
        return self.__command_name

    def __default_command_name(self):
        name_comps = re.findall('[A-Z][^A-Z]*', self.__class__.__name__)
        return '-'.join([x.lower() for x in name_comps])

    def subcommand_name(self):
        return self.__subcommand_name

    def add_subcommand_subparsers(self):
        return self.__arg_parser.add_subparsers(dest=self.subcommand_name(), required=False, metavar="command:")

    def parse_and_invoke(self, args):
        args = self.__arg_parser.parse_args(args)
        self.invoke(args)

    def invoke(self, args=None):
        if args is None:
            args = self.__arg_parser.parse_args()
        subcommand_label = getattr(args, self.subcommand_name())
        if subcommand_label is None:
            self.__arg_parser.print_help()
            exit(0)
        if hasattr(self, subcommand_label):
            field = getattr(self, subcommand_label)
            delattr(args, self.subcommand_name())
            field.invoke(args)
        else:
            print(f"error: Missing field or method '{subcommand_label}' in class {self.__class__.__name__}.")
            exit(-1)
