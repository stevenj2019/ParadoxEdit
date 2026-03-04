import os
from pathlib import Path
# import threading
import concurrent.futures

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericKeyValue
from .ParadoxCategory import GenericCategory
from .ParadoxCategory import EventCategory as Events

implemented_arr = [Events]
#path should point to a descriptor file, 
class ParadoxMod:
    def __init__(self, path:str|os.PathLike):
        path = Path(path)
        self.descriptor_file = path.name
        self.descriptor_object = PDXFile(path)

        self.mod_name:str = ""
        self.mod_base_dir:os.PathLike = None
        self._collect_mod_info()
        if not self.mod_base_dir:
            self.mod_base_dir = path.parent
        
        self.categories:list[GenericCategory] = []
        self.error_categories:list[GenericCategory] = []
        
        self.categories.append(Events(self.mod_base_dir))
        # self._collect_categories()

    def _collect_mod_info(self):
        self.mod_name = next(
            (node.value.value for node in self.descriptor_object.nodes
            if isinstance(node, GenericKeyValue) and node.key == "name"), None
        )
        self.mod_base_dir = next(
            (Path(node.value.value) for node in self.descriptor_object.nodes
            if isinstance(node, GenericKeyValue) and node.key == "file"), None
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