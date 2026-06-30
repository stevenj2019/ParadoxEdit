#Do Not Delete these imports, solves circular imports/"Not Defined" errors
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Contracts import CurrentContext

from App.GUI.Menus import Action
from ParadoxParser.ParadoxNodes import GenericBlock
from App.Contexts.NodeActions import GenericNodeActions, EventBlockActions, EventOptionContext
from App.Contexts.FileActions import ParadoxFileActions, EventFileActions, GFXFileActions
#fill-in till i code ability lol
class CurrentContext:
    def __init__():
        pass

class ParadoxFileContext:
    @staticmethod
    def get_file_context(ctx:CurrentContext, node):
        return ParadoxFileActions
    
    @staticmethod
    def derive_node_context(ctx:CurrentContext, node):
        return GenericNodeActions

class EventFileContext(ParadoxFileContext):
    @staticmethod
    def get_file_context(cts:CurrentContext, node):
        return EventFileActions
    
    @staticmethod
    def derive_node_context(ctx:CurrentContext, node):
        if isinstance(node, GenericBlock):
            if node.key in ["news_event", "country_event"]:
                return EventBlockActions
            elif node.key in ["option", "immediate"]:
                return EventOptionContext
        return GenericNodeActions
    
class GFXFileContext(ParadoxFileContext):
    @staticmethod
    def get_file_context(cts:CurrentContext, node):
        return GFXFileActions
    
    @staticmethod
    def derive_node_context(ctx:CurrentContext, node):
        return GenericNodeActions