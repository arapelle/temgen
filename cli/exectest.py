import sys
from argparse import ArgumentParser
import re

# https://mike.depalatis.net/blog/simplifying-argparse


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


class Temgencmd(CliCommand):
    def __init__(self):
        super().__init__(None, command_name="temgen")
        subparsers = self.add_subcommand_subparsers()
        self.generate = self.Generate(self, subparsers)
        self.config = self.Config(self, subparsers)
        self.cache = self.Cache(self, subparsers)
        self.search = self.Search(self, subparsers)
        self.remove = self.Remove(self, subparsers)

    class Generate(CliCommand):
        def __init__(self, parent: CliCommand, subparsers):
            super().__init__(parent, subparsers=subparsers, help="generate help message")
            self.arg_parser().add_argument("-o", "--output")
            self.arg_parser().add_argument("template_file_path")

        def invoke(self, args=None):
            print(f"Generate.invoke: {args}")

    class Config(CliCommand):
        def __init__(self, parent: CliCommand, subparsers):
            super().__init__(parent, subparsers=subparsers)
            subparsers = self.add_subcommand_subparsers()
            self.list = self.List(self, subparsers)
            self.create = self.Create(self, subparsers)

        class List(CliCommand):
            def __init__(self, parent: CliCommand, subparsers):
                super().__init__(parent, subparsers=subparsers)

            def invoke(self, args=None):
                print(f"List.invoke: {args}")

        class Create(CliCommand):
            def __init__(self, parent: CliCommand, subparsers):
                super().__init__(parent, subparsers=subparsers)
                self.arg_parser().add_argument("config_file_name")

            def invoke(self, args=None):
                print(f"List.invoke: {args}")

    class Cache(CliCommand):
        def __init__(self, parent: CliCommand, subparsers):
            super().__init__(parent, subparsers=subparsers)
            self.arg_parser().add_argument("-v", "--version")
            self.arg_parser().add_argument("template_name")
            self.arg_parser().add_argument("file", nargs="+")

        def invoke(self, args=None):
            print(f"Cache.invoke: {args}")

    class Search(CliCommand):
        def __init__(self, parent: CliCommand, subparsers):
            super().__init__(parent, subparsers=subparsers)
            self.arg_parser().add_argument("-c", "--cache", action="store_true")
            self.arg_parser().add_argument("-r", "--remote")
            self.arg_parser().add_argument("template_id", metavar="template_name[/version]")

        def invoke(self, args=None):
            print(f"Search.invoke: {args}")

    class Remove(CliCommand):
        def __init__(self, parent: CliCommand, subparsers):
            super().__init__(parent, subparsers=subparsers)
            self.arg_parser().add_argument("template_id", metavar="template_name[/version]")

        def invoke(self, args=None):
            print(f"Remove.invoke: {args}")


if __name__ == '__main__':
    temgencmd = Temgencmd()
    program_args = sys.argv
    print(program_args)
    if len(program_args) <= 1:
        temgencmd.parse_and_invoke(program_args[1:])
    else:
        command = program_args[1]
        if command == '-h' or command == '--help' or hasattr(temgencmd, command):
            temgencmd.parse_and_invoke(program_args[1:])
        else:
            temgencmd.parse_and_invoke(["generate"] + program_args[1:])
