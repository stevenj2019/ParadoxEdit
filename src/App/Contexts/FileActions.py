
from App.GUI.Menus import Action
#dumb temporary bullshit
class CurrentContext:
    def __init__():
        pass
def dummy():
    return 
class ParadoxFileActions:
    @staticmethod
    def file_actions(ctx:CurrentContext):
        return [
            Action("Remove Comments", dummy(), False)
        ]
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            Action("Add Comment", dummy(), False)
        ]

class EventFileActions(ParadoxFileActions):
    @staticmethod
    def file_actions(ctx:CurrentContext):
        return [
            *ParadoxFileActions.file_actions(), 
            Action("Inject Event Logs", dummy(), False)
        ]
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            *ParadoxFileActions.node_actions(), 
            Action("Add NameSpace", dummy(), False),
            Action("Add Country Event", dummy(), False),
            Action("Add News Event", dummy(), False)
        ]
    
class GFXFileActions(ParadoxFileActions):
    @staticmethod
    def file_actions(ctx:CurrentContext):
        return [
            *ParadoxFileActions.file_actions()
        ]
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            *ParadoxFileActions.node_actions(),
            Action("Add Static Sprite", dummy(), False),
            Action("Add Animated Sprite", dummy(), False)
       ]
    