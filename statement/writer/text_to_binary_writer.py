import base64

from statement.abstract_statement import AbstractStatement
from statement.writer.apply_strip import apply_strip


class TextToBinaryWriter:
    def __init__(self, output_stream):
        self.__output_stream = output_stream

    def execute(self, input_contents: str, statement: AbstractStatement):
        default_format_attr = "format"
        node = statement.current_node()
        format_action = statement.format_str(node.get("format", default_format_attr))
        default_strip_attr = "strip" if format_action == "base64" or format_action == "base64-url" else "strip-hs"
        strip_attr = node.get("strip", default_strip_attr)
        strip_action = statement.format_str(strip_attr)
        input_contents = apply_strip(input_contents, strip_action)
        input_contents = self.__apply_format(input_contents, format_action, statement)
        self.__output_stream.write(input_contents)

    def __apply_format(self, input_contents: str, format_action: str, statement: AbstractStatement):
        match format_action:
            case "raw":
                return input_contents
            case "format":
                return statement.format_str(input_contents)
            case "base64":
                return base64.standard_b64decode(input_contents)
            case "base64-url":
                return base64.urlsafe_b64decode(input_contents)
            case _:
                raise RuntimeError(f"Unknown format action : {format_action}.")
