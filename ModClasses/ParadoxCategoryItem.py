from ParadoxParser import ParadoxScriptParser as PDXFile
from ModClasses.util import Action
from Backend.Generic import clear_comments, clear_whitespace
from Backend.Events import event_log_injection
class GenericCategoryItem:
    @classmethod
    def context_sections(cls):
        return { 
            "PDX Script Options": [
                Action("Clear Comments", clear_comments),
                Action("Clear Whitespace", clear_whitespace)
            ]
        }
    def __init__(self, pdx_obj:PDXFile):
        self.obj = pdx_obj
        self.has_been_modified:bool = False

class EventCategoryItem(GenericCategoryItem):
    @classmethod
    def context_sections(cls):
        return {
            **super().context_sections(),
            "Event Options":[
                Action("Inject Logs", event_log_injection)
            ]
        }

    def __init__(self, pdx_obj:PDXFile):
        super().__init__(pdx_obj)
        