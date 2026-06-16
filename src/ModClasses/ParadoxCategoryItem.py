from ParadoxParser import ParadoxScriptParser as PDXFile
from ModClasses.util import Action
from Backend.Generic import clear_comments, clear_whitespace, save_file
from Backend.Events import event_log_injection
from Backend import Generic, Events, GFX
class GenericCategoryItem:
    def __init__(self, pdx_obj:PDXFile):
        self.obj = pdx_obj
        self.has_been_modified:bool = False

    def context_sections(self):
        return { 
            "PDX Script Options": [
                Action("Save Changes", save_file, self.has_been_modified),
                Action("Clear Comments", Generic.clear_comments, True),
                Action("Clear Whitespace", Generic.clear_whitespace, True)
            ]
        }

class EventCategoryItem(GenericCategoryItem):
    def __init__(self, pdx_obj:PDXFile):
        super().__init__(pdx_obj)
        
    def context_sections(self):
        return {
            **super().context_sections(),
            "Event Options":[
                Action("Inject Logs", Events.event_log_injection, False)#doesnt work right
            ]
        }
        
class GFXCategoryItem(GenericCategoryItem):
    def __init__(self, pdx_obj:PDXFile):
        super().__init__(pdx_obj)

    def context_sections(self):
        return {
            **super().context_sections(), 
            "GFX Options":[
                Action("Add New GFX", GFX.add_new_GFX, False),#not implemented
                Action("Add missing _shines", GFX.add_missing_shines, True) #not implemented
            ]
        }