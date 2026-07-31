from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.LoadOrder import ParadoxLoadOrder
    from App.Services import Workspace


import logging
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent
import platform

from platformdirs import user_log_dir
from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
import psutil

from App.Contracts.Enums import ChangeState
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode
from App.AppData import APPNAME, VERSION, COMMIT


class AppLogger:
    _logger = logging.getLogger(APPNAME)

    @classmethod
    def initialise(cls) -> None:
        log_directory = Path(user_log_dir(APPNAME))
        log_directory.mkdir(parents=True, exist_ok=True)
        log_file = log_directory / f"{APPNAME}.log"

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

    @classmethod
    def raw(cls, message: str) -> None:
        for handler in cls._logger.handlers:
            handler.acquire()
            try:
                handler.stream.write(message + "\n")
                handler.flush()
            finally:
                handler.release()

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

    @classmethod
    def application_metadata_logger(cls) -> None:
        cls.raw(dedent(
            f"""
            ############################
            ##  Application Metadata  ##
            ############################
            Name:          {APPNAME}
            Version:       {VERSION}
            Commit:        {COMMIT}
            """))

    @classmethod
    def runtime_metadata_logger(cls) -> None:
        cls.raw(dedent(
            f"""
            ########################
            ##  Runtime Metadata  ##
            ########################
            PythonVersion: {platform.python_version()}
            QtVersion:     {QT_VERSION_STR}
            PyQtVersion:   {PYQT_VERSION_STR}
            DateTime:      {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}
            Platform:      {platform.platform()}
            Architecture:  {platform.architecture()[0]}
            CPUCores(P):   {psutil.cpu_count(logical=False)}
            CPUCores(L):   {psutil.cpu_count(logical=True)}
            Memory:        {round(psutil.virtual_memory().total / (1024 ** 3), 2)}
            ProcessMemory: {round(psutil.Process().memory_info().rss / (1024 ** 3), 2)} GiB
            """))

    @classmethod
    def workspace_metadata_logger(cls, workspace:Workspace, load_order:ParadoxLoadOrder) -> None:
        cls.raw(dedent(
            f"""
            ##########################
            ##  Workspace Metadata  ##
            ##########################
            VanillaLoad:   {workspace.vanilla_loaded}
            Mods:          {len(workspace.mods)}
            ProcessMemory: {round(psutil.Process().memory_info().rss / (1024 ** 3), 2)} GiB
            LoadOrder:"""
        ))
        for index, source in enumerate(load_order.sources):
            cls.raw(f"  {index+1}. {source.source_name}")