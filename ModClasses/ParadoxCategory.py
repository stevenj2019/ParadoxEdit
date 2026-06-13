import os 
from pathlib import Path
from ParadoxParser.ParadoxNodes import GenericNode, GenericBlock, GenericKeyValue
from ParadoxParser import ParadoxScriptParser as PDXFile

class GenericCategory:
    def __init__(self, base:os.PathLike, paths:list[os.PathLike]):
        # self.files:list[PDXFile] = []
        self.files:dict[str, PDXFile] = {}
        # self.category_data:dict[str, PDXFile] = {}
        for path in paths:
            self._read_directory(os.path.join(base, path))

    def _read_file(self, file):
        self._parse_file(file)
        
    #default is to collect all. path is wrong lol
    def _read_directory(self, path):
        for root, dirs, files in os.walk(path):
            for name in dirs:
                self._read_directory(Path(os.path.join(root, name)))
            for name in files:
                self._parse_files(Path(os.path.join(root, name)))

    def _parse_files(self, path:os.PathLike)->PDXFile:
        self.files[path.name] = PDXFile(path)
        # self.files.append(PDXFile(path))
    
    # def _organise(self)->GenericBlock:
        # self.category_data = { f.filename: f for f in self.files }
        # return 
    
    def _context_menu_items():
        return

#can do now
# class HistoryCategory() history/
# need imageviewer/dds viewer
# class gfx/

EVENT_ERROR_KEYS = ("missing_data", "missing_id", "missing_namespace") 
class EventCategory(GenericCategory):
    def __init__(self, mod_path:os.PathLike):
        super().__init__(mod_path, ["events/"])