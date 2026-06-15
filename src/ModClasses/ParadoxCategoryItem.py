from ParadoxParser import ParadoxScriptParser as PDXFile
from ModClasses.util import Action
from Backend.Generic import clear_comments, clear_whitespace, save_file
from Backend.Events import event_log_injection
class GenericCategoryItem:
    def __init__(self, pdx_obj:PDXFile):
        self.obj = pdx_obj
        self.has_been_modified:bool = False

    def context_sections(self):
        return { 
            "PDX Script Options": [
                # Action("Save Changes", save_file, self.has_been_modified),
                Action("Clear Comments", clear_comments, True),
                Action("Clear Whitespace", clear_whitespace, True)
            ]
        }

class EventCategoryItem(GenericCategoryItem):
    def __init__(self, pdx_obj:PDXFile):
        super().__init__(pdx_obj)
        
    def context_sections(self):
        return {
            **super().context_sections(),
            "Event Options":[
                Action("Inject Logs", event_log_injection, True)
            ]
        }
        