from ParadoxParser import ParadoxScriptParser as PDXScriptFile
# from App.ModClasses.ActionModels import ActionGroup, Action
from App.Backend import Generic, Events, GFX

class GenericCategoryItem:
    def __init__(self, pdx_obj:PDXScriptFile):
        self.obj = pdx_obj
        self.has_been_modified:bool = False
        
    # def context_sections(self):
    #     return [
    #         ActionGroup("PDX Script Options", [
    #             Action("Clear Comments", Generic.clear_comments, True),
    #             Action("Clear Whitespace", Generic.clear_whitespace, True)
    #         ])
    #     ]

class EventCategoryItem(GenericCategoryItem):
    def __init__(self, pdx_obj:PDXScriptFile):
        super().__init__(pdx_obj)
        
    # def context_sections(self):
    #     return [
    #         *super().context_sections(),
    #         # "Event Options":[
    #         #     Action("Inject Logs", Events.event_log_injection, False)#doesnt work right
    #         # ]
    #     ]
        
class GFXCategoryItem(GenericCategoryItem):
    def __init__(self, pdx_obj:PDXScriptFile):
        super().__init__(pdx_obj)

    # def context_sections(self):
    #     return [
    #         *super().context_sections(), 
    #         # "GFX Options":[
    #         #     Action("Add New GFX", GFX.add_new_GFX, True),
    #         #     Action("Add missing _shines", GFX.add_missing_shines, True)
    #         # ]
    #     ]