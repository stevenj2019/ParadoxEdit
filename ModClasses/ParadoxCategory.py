import os 
from ParadoxParser.ParadoxNodes import GenericNode, GenericBlock
from ParadoxParser import ParadoxScriptParser as PDXFile

#lol, so this, and all these, need a base path....
class GenericCategory:
    def __init__(self, base:os.PathLike, paths:list[os.PathLike]):
        self.files:list[PDXFile] = []
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
    
    def _organise(self):
        return {file.filename: file for file in self.files}
        
class EventCategory(GenericCategory):
    def __init__(self, mod_path:os.PathLike):
        super().__init__(mod_path, ["events/"])
        self.namespaces:list[str] = []
        self.category_data:dict[str, GenericNode]= {}
        self.errors:dict[str, str] = {}
        self.errors["missing_namespace"] = {}
        self.error_overflow:list[GenericNode] = {}

    def _organise(self):
        namespace_found = []
        for file in self.files:
            for node in file.nodes:
                if node.key == "add_namespace":
                    if node.value.value not in self.namespaces:
                        self.name_spaces.append(node.value.value)
                if "_event" in node.key:
                    event_id = next((child.key for child in node.children if child.key=="id"), None)
                    event_namespace = event_id.split(".")[0]
                    if not event_namespace in self.category_data.keys():
                        self.category_data[event_namespace] = {}
                    if event_id not in self.category_data[event_namespace].keys():
                        self.category_data[event_namespace][event_id] = node
                    else:
                        self.error_overflow.append(node)
                #can only be a comment, in this case, we dont really care about them? 

        for namespace in self.category_data.keys():
            if namespace not in namespace_found:
                self.errors["missing_namespace"].append(f"{namespace} is never declared")
