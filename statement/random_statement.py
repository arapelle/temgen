import random
import xml.etree.ElementTree as XMLTree
from builtins import RuntimeError
from io import IOBase, StringIO, BytesIO

import random_string
from log import MethodScopeLog
from statement.abstract_main_statement import AbstractMainStatement
from statement.abstract_statement import AbstractStatement


class RandomStatement(AbstractMainStatement):
    def __init__(self, current_node: XMLTree.Element, parent_statement: AbstractStatement,
                 io_stream: IOBase | None, **kargs):
        super().__init__(current_node, parent_statement, **kargs)
        self.__io_stream = io_stream

    def io_stream(self):
        return self.__io_stream

    def execute(self):
        with MethodScopeLog(self):
            random_value = self.__try_random_value_from_type()
            if random_value is None:
                random_value = self.__try_random_value_from_set()
            if random_value is not None:
                self.__io_stream.write(random_value)
            else:
                raise RuntimeError("One of the following attribute is missing for random statement: "
                                   "type, char-set.")

    def __build_string_stream_if_missing(self):
        if self.__io_stream is None:
            self.__io_stream = StringIO()

    def __build_bytes_stream_if_missing(self):
        if self.__io_stream is None:
            self.__io_stream = BytesIO()

    def __try_random_value_from_type(self):
        value_type = self.current_node().attrib.get("type", None)
        if value_type is None:
            return None
        self.__build_string_stream_if_missing()
        rand_fn_name = f"random_{value_type}_string"
        try:
            rand_fn = getattr(self, rand_fn_name)
            return rand_fn(self.current_node())
        except AttributeError:
            pass
        try:
            rand_fn = getattr(random_string, rand_fn_name)
            max_len, min_len = self.__get_min_max_len(self.current_node())
            return rand_fn(min_len, max_len)
        except AttributeError:
            raise RuntimeError(f"Bad value type: '{value_type}'.")

    def __try_random_value_from_set(self):
        element_set = self.current_node().attrib.get("char-set", None)
        rand_fn = random_string.random_string
        if element_set is not None:
            self.__build_string_stream_if_missing()
            max_len, min_len = self.__get_min_max_len(self.current_node())
            return rand_fn(element_set, min_len, max_len)
        return None

    @staticmethod
    def __get_min_max_len(random_node):
        length = random_node.attrib.get("len", None)
        if length is not None:
            length = int(length)
            return length, length
        min_len = int(random_node.attrib.get("min-len", 0))
        max_len = int(random_node.attrib.get("max-len"))
        if min_len > max_len:
            raise RuntimeError(f"In random, min-len ({min_len}) must be less than max-len ({max_len}).")
        return max_len, min_len

    @staticmethod
    def random_int_string(rand_value_node: XMLTree.Element):
        min_value = int(rand_value_node.attrib.get("min", 0))
        max_value = int(rand_value_node.attrib.get("max"))
        if min_value > max_value:
            raise RuntimeError(f"In random, min ({min_value}) must be less than max ({max_value}).")
        return str(random.randint(min_value, max_value))

    @staticmethod
    def random_float_string(rand_value_node: XMLTree.Element):
        min_value = float(rand_value_node.attrib.get("min", 0))
        max_value = float(rand_value_node.attrib.get("max"))
        if min_value > max_value:
            raise RuntimeError(f"In random, min ({min_value}) must be less than max ({max_value}).")
        return f"{random.uniform(min_value, max_value):.3f}"

    @staticmethod
    def random_format_cvqd_string(rand_value_node: XMLTree.Element):
        fmt_str = rand_value_node.attrib.get("fmt")
        return random_string.random_format_cvqd_string(fmt_str)
