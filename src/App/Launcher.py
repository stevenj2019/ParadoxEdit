# from __future__ import annotations

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from App import AppController


# from App.AppData import APPNAME


# from pathlib import Path
# from platformdirs import user_config_dir
# import json
# import subprocess
# import threading

# class ParadoxProcess:
#     def __init__(self, 
#                  app_controller:AppController,
#                  configuration:Path,
#                  callback:callable
#                  ) -> None:
#         self.app_controller = app_controller,
#         self.workspace = self.app_controller.file_system.workspace
#         self.callback = callback
#         self.process_configuration = ProcessConfiguration(configuration)
#         #later
#         self.process:subprocess.Popen|None = None
#         self.tripwires:TripWireConfiguration|None = None
#         self.error_filters:ErrorFilterConfiguration|None = None

#     def start(self)-> None:
#         self.process = subprocess.Popen(
#             self.process_configuration.get_start_command(),
#             cwd=self.process_configuration.get_cwd(),
#             stdin=subprocess.DEVNULL,
#             stdout=subprocess.DEVNULL
#         )
#         threading.Thread(self.watch_process, daemon=True)

#     def _teardown(self)->None:
#         if self.error_filters:
#             self.format_error_log()

#     def watch_process(self) -> None:
#         self.process.wait()
#         self._teardown()

#     def stop(self)->None:
#         self.process.terminate()
#         try:
#             self.process.wait(timeout=5)
#         except subprocess.TimeoutExpired:
#             self.process.kill()
#             self.process.wait()

#     def format_error_log(self) -> None:
#         return #code to filter error logs

    
# class ProcessConfiguration:
#     def __init__(self, config:Path) -> None:
#         self.config = json.loads(config.read_bytes())
#         self.executable = self._get_executable()
#         self.load_args = [self._resolve_arg(k, v) for k, v in self.config["launch_args"].keys()]

#     def _get_executable(self)-> str:
#         if "executable" in self.config:
#             return self.config["executable"]
#         return user_config_dir(APPNAME) + "configuration.json"

#     def _resolve_arg(self, arg:str, value:str|bool) -> list[str]:
#         return f"-{arg}" if isinstance(value, bool) else f"-{arg}={value}"

#     #add any commands which call for an early, unprompted termination.
#     def tripwires(self) -> list[str]:
#         return 
    
#     def _to_json(self) -> dict:
#         return {
#             "executable":str(self.executable),
#             "launch_args": {}
#         }

#     #serialise configuration.
#     def write_file(self) -> None:
#         return 

# class ErrorFilterConfiguration:
#     def __init__(self, filters:list[ErrorFilter]) -> None:
#         self.error_filters = filters
#     # def apply_filters(self):
#     #     for filter in self.error_filters:
#     #         match/case of Enums
#     #            case whatever: get error.log, apply filter

# # class ErrorFilter(Enum):
# #     HIDE_TAG = auto()

# class TripWireConfiguration:
#     def __init__(self, tripwires:list[TripWires])-> None:
#         self.tripwires = tripwires

# # class TripWires(Enum):
# #     GAME_START = "End RestoreDeviceObjects"