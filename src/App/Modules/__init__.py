import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericKeyValue
from App.Modules.Base import GenericCategory

# implemented_arr = [EventCategory, GFXCategory]
class ParadoxMod:
    def __init__(self, path:str|os.PathLike):
        path = Path(path)
        self.descriptor_file = path.name
        self.descriptor_object = PDXScriptFile(path)

        self.mod_name:str = ""
        self.mod_base_dir:os.PathLike = None
        self._collect_mod_info()
        if not self.mod_base_dir:
            self.mod_base_dir = path.parent
        
        self.categories:dict[str, GenericCategory] = {}
        self.error_categories:list[GenericCategory] = []


        from App.Modules._Registry import IMPLEMENTED
        for category in IMPLEMENTED:
            obj = category(self.mod_base_dir)
            self.categories[type(obj).__name__] = obj

    def _collect_mod_info(self):
        self.mod_name = next(
            (node.value.value for node in self.descriptor_object.nodes
            if isinstance(node, GenericKeyValue) and node.key == "name"), None
        )
        self.mod_base_dir = next(
            (Path(node.value.value.strip('"')) for node in self.descriptor_object.nodes
            if isinstance(node, GenericKeyValue) and node.key == "path"), None
        )

    def _resolve_path(self, path):
        return self.mod_base_dir / path
