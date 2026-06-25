import os
from pathlib import Path
# import threading
import concurrent.futures

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericKeyValue, GenericNode
from .CategoryItems import GenericCategoryItem
from .Categories import GenericCategory
from .Categories import EventCategory as Events
from .Categories import GFXCategory as GFX
implemented_arr = [Events, GFX]
#path should point to a descriptor file, 

class ParadoxMod:
    def __init__(self, path:str|os.PathLike):
        path = Path(path)
        self.descriptor_file = path.name
        self.descriptor_object = GenericCategoryItem(PDXFile(path))

        self.mod_name:str = ""
        self.mod_base_dir:os.PathLike = None
        self._collect_mod_info()
        if not self.mod_base_dir:
            self.mod_base_dir = path.parent
        
        self.categories:dict[str, GenericCategory] = {}
        self.error_categories:list[GenericCategory] = []

        for category in implemented_arr:
            obj = category(self.mod_base_dir)
            # obj._organise()
            self.categories[type(obj).__name__] = obj

    def iter_file(self):
        files = []
        for category in self.categories:
            for file in category.iter_files():
                files.expand(file)
        return files
    
    def _get_saving_targets(self, modified_only:bool = True):
        save_targets = []
        for category in self.categories:
            for file in category.iter_files():
                if file.has_been_modified:
                    save_targets.append(file)

    def _collect_mod_info(self):
        self.mod_name = next(
            (node.value.value for node in self.descriptor_object.obj.nodes
            if isinstance(node, GenericKeyValue) and node.key == "name"), None
        )
        self.mod_base_dir = next(
            (Path(node.value.value.strip('"')) for node in self.descriptor_object.obj.nodes
            if isinstance(node, GenericKeyValue) and node.key == "path"), None
        )
    # def _collect_categories(self):
    #     def init_category(CategoryClass):
    #         try:
    #             return CategoryClass()  # instantiate category
    #         except Exception as e:
    #             print(f"Failed to load {CategoryClass.__name__}: {e}")
    #             return None

    #     with concurrent.futures.ThreadPoolExecutor() as executor:
    #         # map the Category classes to the executor
    #         results = executor.map(init_category, implemented_arr)

    #     # append only successful objects
    #     for obj, cls in zip(results, implemented_arr):
    #         if obj is not None:
    #             self.categories.append(obj)
    #         else:
    #             self.error_categories.append(cls.__name__)