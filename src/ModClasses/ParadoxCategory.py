import os 
from pathlib import Path
from ParadoxParser.ParadoxNodes import GenericNode, GenericBlock, GenericKeyValue
from .ParadoxCategoryItem import GenericCategoryItem, EventCategoryItem
from ParadoxParser import ParadoxScriptParser as PDXFile
from ModClasses.util import Action
from Backend.Generic import clear_comments, clear_whitespace
from Backend.Events import event_log_injection
class GenericCategory:
    @classmethod
    def context_sections(cls):        
        return { 
            "PDX Script Options": [
                Action("Clear Comments", clear_comments),
                Action("Clear Whitespace", clear_whitespace)
            ]
        }
    
    def __init__(self, base:os.PathLike, paths:list[os.PathLike], item_class:GenericCategoryItem):
        self.item_class = item_class
        self.files:dict[str, GenericCategoryItem] = {}
        for path in paths:
            self._read_directory(os.path.join(base, path))

    def _read_file(self, file):
        self._parse_file(file)
        
    def _read_directory(self, path):
        for root, dirs, files in os.walk(path):
            for name in dirs:
                self._read_directory(Path(os.path.join(root, name)))
            for name in files:
                self._parse_files(Path(os.path.join(root, name)))

    def _parse_files(self, path:os.PathLike)->GenericCategoryItem:
        self.files[path.name] = self.item_class(PDXFile(path))

#can do now
# class HistoryCategory() history/
# need imageviewer/dds viewer
# class gfx/

EVENT_ERROR_KEYS = ("missing_data", "missing_id", "missing_namespace") 
class EventCategory(GenericCategory):
    @classmethod
    def context_sections(cls):
        return {
            **super().context_sections(),
            "Event Options":[
                Action("Inject Logs", event_log_injection)
            ]
        }
    def __init__(self, mod_path:os.PathLike):
        super().__init__(mod_path, ["events/"], EventCategoryItem)