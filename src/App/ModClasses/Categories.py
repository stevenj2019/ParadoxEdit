import os 
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXFile

from App.ModClasses.FileContexts import ParadoxFileContext, EventFileContext, GFXFileContext
from App.ModClasses.ActionModels import ActionGroup, Action
from App.Backend import Generic, Events

class GenericCategory:
    def __init__(self, base:os.PathLike, paths:list[os.PathLike], context:ParadoxFileContext, file_type:str=None):
        self.file_type = file_type
        self.context:ParadoxFileContext = context
        self.files:dict[str, PDXFile] = {}
        for path in paths:
            self._read_directory(os.path.join(base, path))

    def context_sections(self):
        return [
            ActionGroup("PDX Script Options", [
                Action("Clear Comments", Generic.clear_comments, True),
                Action("Clear Whitespace", Generic.clear_whitespace, True)
            ])
        ]
    
    def _read_file(self, file):
        self._parse_file(file)
        
    def _read_directory(self, path):
        for root, dirs, files in os.walk(path):
            for name in dirs:
                self._read_directory(Path(os.path.join(root, name)))
            for name in files:
                if ((not self.file_type or name.endswith(self.file_type)) 
                     and not name.endswith(".bak")):
                    self._parse_files(Path(os.path.join(root, name)))

    def _parse_files(self, path:os.PathLike):
        self.files[path.name] = PDXFile(path)

# EVENT_ERROR_KEYS = ("missing_data", "missing_id", "missing_namespace") might do, might not
class EventCategory(GenericCategory):
    def __init__(self, mod_path:os.PathLike):
        super().__init__(mod_path, ["events/"], EventFileContext)

    def context_sections(self):
        return [
            *super().context_sections(),
            # "Event Options":[
            #     Action("Inject Logs", Events.event_log_injection, False)#doesnt work right
            # ]
        ]
    
class GFXCategory(GenericCategory):
    def __init__(self, mod_path:os.PathLike):
        super().__init__(mod_path, ["interface/"], GFXFileContext, ".gfx")

    def context_sections(self):
        return [
            *super().context_sections()
        ]