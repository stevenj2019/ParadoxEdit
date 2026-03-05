import os 
from pathlib import Path
from ParadoxParser.ParadoxNodes import GenericNode, GenericBlock, GenericKeyValue
from ParadoxParser import ParadoxScriptParser as PDXFile

class GenericCategory:
    def __init__(self, base:os.PathLike, paths:list[os.PathLike]):
        self.files:list[PDXFile] = []
        self.category_data:dict[str, PDXFile] = {}
        for path in paths:
            self._read_directory(os.path.join(base, path))

    def _read_file(self, file):
        self._parse_file(file)
        
    #default is to collect all.
    def _read_directory(self, path):
        for root, dirs, files in os.walk(path):
            for name in dirs:
                self._read_directory(os.path.join(root, name))
            for name in files:
                self._parse_files(os.path.join(root, name))

    def _parse_files(self, path:os.PathLike)->PDXFile:
        self.files.append(PDXFile(path))
    
    def _organise(self)->GenericBlock:
        self.category_data = { f.filename: f for f in self.files }
        # return {file.filename: file for file in self.files}
        return 
    
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
        # self.namespaces:list[str] = []
        # self.sorted_by_ns:bool = False
        # self.category_data:dict[str, PDXFile]= {}
        # self.errors:dict[str, str] = {}
        # self.errors["missing_namespace"] = {}
        # self.error_overflow:list[GenericNode] = {}

    #i think this is where the issue is, 
    #if they are by filename (default) i should load them in the left individually
    #if by namespace i should populate a list with the namepaced for the left, 
    # and reorganise the current event nodes into individual GenericBlocks, 
    # to correctly render the individual elements (keeping the reference hopefully)
    # def _get_not_sort_by_text(self):
    #     return "file" if self.sorted_by_ns else "namespace"
    
    # def _organise(self, by_namespace:bool = False):
    #     self.sorted_by_ns:bool = by_namespace
    #     self.category_data:dict[str, GenericNode]= {}
    #     self.errors = {k: [] for k in EVENT_ERROR_KEYS}
    #     if by_namespace:
    #         for file in self.files:
    #             for node in file.nodes:
    #                 if isinstance(node, GenericBlock) or isinstance(node, GenericKeyValue):
    #                     if node.key == "add_namespace":
    #                         if node.value.value not in self.category_data:
    #                             self.category_data[node.value.value] = DummyPDXFile(name=node.value.value)
    #                     elif "_event" in node.key:
    #                         event_id = next(
    #                             (child.value.value for child in node.children if hasattr(child, "key") and child.key=="id"), 
    #                             None
    #                         )
    #                         if event_id:
    #                             event_namespace = event_id.split(".")[0]
    #                             if event_namespace not in self.category_data.keys():
    #                                 self.category_data[event_namespace] = DummyPDXFile(name=event_namespace)
                                
    #                             self.category_data[event_namespace].nodes.append(node)
                                
    #                         else:
    #                             self.errors["missing_id"].append(node)
    #                             continue
                                
    #     else:
    #         # self.category_data = GenericBlock(self.filename)
    #         self.category_data = {f.filename: f for f in self.files}
    
