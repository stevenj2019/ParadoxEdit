from ParadoxParser import ParadoxScriptParser as PDXScriptFile

class GenericCategoryItem:
    def __init__(self, pdx_obj:PDXScriptFile):
        self.obj = pdx_obj
        self.has_been_modified:bool = False

class EventCategoryItem(GenericCategoryItem):
    def __init__(self, pdx_obj:PDXScriptFile):
        super().__init__(pdx_obj)

class GFXCategoryItem(GenericCategoryItem):
    def __init__(self, pdx_obj:PDXScriptFile):
        super().__init__(pdx_obj)
