from statement.abstract_statement import AbstractStatement


class BinaryToBinaryWriter:
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
        default_format_attr = "raw"
        format_attr = statement.current_node().get("format", default_format_attr)
        format_action = statement.format_str(format_attr)
        match format_action:
            case "raw":
                return input_contents
            case _:
                raise RuntimeError(f"Unknown format action : {format_action}.")
