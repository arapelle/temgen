from statement.abstract_statement import AbstractStatement
from statement.writer.apply_strip import apply_strip


class TextToTextWriter:
    def __init__(self, output_stream):
        self.__output_stream = output_stream

    def execute(self, input_contents: str, statement: AbstractStatement):
        default_strip_attr = "strip-hs"
        strip_attr = statement.current_node().get("strip", default_strip_attr)
        strip_action = statement.format_str(strip_attr)
        input_contents = apply_strip(input_contents, strip_action)
        input_contents = self.__apply_format(input_contents, statement)
        self.__output_stream.write(input_contents)

    def __apply_format(self, input_contents: str, statement: AbstractStatement):
        default_format_attr = "format"
        format_attr = statement.current_node().get("format", default_format_attr)
        format_action = statement.format_str(format_attr)
        match format_action:
            case "raw":
                return input_contents
            case "format":
                return statement.format_str(input_contents)
            case _:
                raise RuntimeError(f"Unknown format action : {format_action}.")
