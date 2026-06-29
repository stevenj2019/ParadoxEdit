import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericKeyValue
from App.ModClasses.CategoryItems import GenericCategoryItem
from App.ModClasses.Categories import GenericCategory
from App.ModClasses.Categories import EventCategory as Events
from App.ModClasses.Categories import GFXCategory as GFX
implemented_arr = [Events, GFX]

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

        for category in implemented_arr:
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
        # self.mod_name = next(
        #     (node.value.value for node in self.descriptor_object.obj.nodes
        #     if isinstance(node, GenericKeyValue) and node.key == "name"), None
        # )
        # self.mod_base_dir = next(
        #     (Path(node.value.value.strip('"')) for node in self.descriptor_object.obj.nodes
        #     if isinstance(node, GenericKeyValue) and node.key == "path"), None
        # )
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