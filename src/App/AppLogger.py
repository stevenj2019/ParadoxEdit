import logging
import sys
from datetime import datetime
from pathlib import Path

from platformdirs import user_log_dir

from App.Contracts.Enums import ChangeState
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode

app_name = "PDXEdit"
class AppLogger:
    _logger = logging.getLogger(app_name)

    @classmethod
    def initialise(cls) -> None:
        log_directory = Path(user_log_dir(app_name))
        log_directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = log_directory / f"{app_name}-{timestamp}.log"

        cls._logger.setLevel(logging.DEBUG)
        if cls._logger.handlers:
            return

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        # file out
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        cls._logger.addHandler(file_handler)
        # console out
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)
        cls.info(f"Logging initialised: {log_file}")

    @classmethod
    def debug(cls, message: str) -> None:
        cls._logger.debug(cls._format(message))

    @classmethod
    def info(cls, message: str) -> None:
        cls._logger.info(cls._format(message))

    @classmethod
    def warning(cls, message: str) -> None:
        cls._logger.warning(cls._format(message))

    @classmethod
    def error(cls, message: str) -> None:
        cls._logger.error(cls._format(message))

    @classmethod
    def exception(cls, exc: Exception) -> None:
        cls._logger.exception(exc)

    @classmethod
    def mutation(cls, node: GenericNode, state: ChangeState) -> None:
        cls.info(f"Setting {cls._format(node)} -> {state}")

    @staticmethod
    def _format(obj: GenericNode | PDXScriptFile | PDXLocFile) -> None:
        if isinstance(obj, (PDXScriptFile, PDXLocFile)):
            return f"{obj.filename}"

        if isinstance(obj, GenericBlock):
            return f"{obj.key} {{...}}"

        if isinstance(obj, GenericKeyValue):
            return f"{obj.key} = {obj.value}"

        if isinstance(obj, GenericNode):
            return str(obj.value)

        return str(obj)