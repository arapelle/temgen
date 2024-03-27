import base64

from statement.abstract_statement import AbstractStatement


class BinaryToTextWriter:
    def __init__(self, output_stream):
        self.__output_stream = output_stream

    def execute(self, input_contents: bytes, statement: AbstractStatement):
        input_contents = self.__apply_strip(input_contents, statement)
        input_contents = self.__apply_format(input_contents, statement)
        self.__output_stream.write(input_contents)

    def __apply_strip(self, input_contents: bytes, statement: AbstractStatement):
        assert "strip" not in statement.current_node().attrib
        return input_contents

    def __apply_format(self, input_contents: bytes, statement: AbstractStatement):
        default_format_attr = "base64"
        format_attr = statement.current_node().get("format", default_format_attr)
        format_action = statement.format_str(format_attr)
        match format_action:
            case "base64":
                return str(base64.standard_b64encode(input_contents))
            case "base64-url":
                return str(base64.urlsafe_b64encode(input_contents))
            case _:
                raise RuntimeError(f"Unknown format action : {format_action}.")
