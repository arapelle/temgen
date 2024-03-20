import logging
import os
import platform
from datetime import datetime
from pathlib import Path


def tmp_dirpath():
    platform_system = platform.system().strip().lower()
    match platform_system:
        case "windows":
            return Path(f"{os.environ['TMP']}")
        case "linux":
            return Path(f"/tmp")
        case _:
            raise Exception(f"System not handled: '{platform_system}'")


def tool_tmp_dirpath(tool_name: str):
    return tmp_dirpath() / f"{tool_name}"


def tool_log_dirpath(tool_name: str):
    return tmp_dirpath() / f"{tool_name}/log"


class LoggerMaker:
    def __init__(self, **kwargs):
        tool_name = kwargs.get("tool")
        log_filestem = tool_name if tool_name is not None else "logfile"
        if "dir" in kwargs:
            log_dir = Path(kwargs.get("dir"))
        elif "tool" in kwargs:
            log_dir = tool_log_dirpath(log_filestem)
        else:
            raise RuntimeError("'dir' or 'tool' is missing as named argument.")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_filename = datetime.now().strftime(f"{log_filestem}_%Y%m%d_%H%M%S_%f.log")
        log_filename = kwargs.get("filename", log_filename)
        self.__log_filepath = Path(f"{log_dir}/{log_filename}")

    def log_filepath(self):
        return self.__log_filepath

    def make_console_file_logger(self):
        file_format = "[%(levelname)-8s][%(asctime)s][%(pathname)s:%(lineno)d %(funcName)s]: %(message)s"
        logging.basicConfig(filename=self.__log_filepath,
                            level=logging.DEBUG,
                            format=file_format,
                            filemode='w',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            force=True)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = "[%(levelname)-8s][%(asctime)s][%(filename)s:%(lineno)d]: %(message)s"
        formatter = logging.Formatter(console_format)
        console_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(console_handler)
        return logger


def make_console_file_logger(**kwargs):
    logger_maker = LoggerMaker(**kwargs)
    logger = logger_maker.make_console_file_logger()
    log_to_info = kwargs.get("log_to_info", False)
    if log_to_info:
        logger.info(f"Log to {logger_maker.log_filepath()}")
    return logger
