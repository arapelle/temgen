import sys

from util.cli_command import CliCommand


# https://mike.depalatis.net/blog/simplifying-argparse


class CliTemgen(CliCommand):
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
    temgencmd = CliTemgen()
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
