#Do Not Delete these imports, solves circular imports/"Not Defined" errors
from __future__ import annotations
from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from App.Contracts import CurrentContext
#     from App.ModClasses.FileContexts import ParadoxFileContext
# from App.Contracts import CurrentContext

from App.GUI.Menus import Action
from App.Contexts.FileActions import ParadoxFileActions
#dumb temporary bullshit
class CurrentContext:
    def __init__():
        pass
def dummy():
    return 

###       ###
#  GENERIC  #
###       ###
class GenericNodeActions:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return []
    
###          ###
#  PRE-BUILTS  #
###          ###
class EffectsContext:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
           Action("EffectsContext", dummy(), False)
        ]
    
class TriggersContext:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            Action("TriggersContext", dummy(), False)
        ]
    
###      ###
#  EVENTS  #
###      ###
class EventBlockContext:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            *ParadoxFileActions.node_actions(ctx), 
            Action("EventBlockContext", dummy(), False)
            # Action("Add Immediate Block", dummy(), False),
            # Action("Add Option Block", dummy(), False)
        ]
    
class EventOptionContext:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            *ParadoxFileActions.node_actions(ctx),
            *TriggersContext.node_actions(ctx), 
            *EffectsContext.node_actions(ctx),
        ]
