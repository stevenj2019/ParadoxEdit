#Do Not Delete these imports, solves circular imports/"Not Defined" errors
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Contracts import CurrentContext

from ParadoxParser.ParadoxNodes import GenericBlock
from App.Contexts.NodeActions import GenericNodeActions, EventBlockActions, EventOptionContext
from App.Contexts.FileActions import ParadoxFileActions, EventFileActions, GFXFileActions

class ParadoxFileContext:
    @staticmethod
    def get_file_context():
        return ParadoxFileActions
    
    @staticmethod
    def derive_node_context(node):
        return GenericNodeActions

class EventFileContext(ParadoxFileContext):
    @staticmethod
    def get_file_context():
        return EventFileActions
    
    @staticmethod
    def derive_node_context(node):
        if isinstance(node, GenericBlock):
            if node.key in ["news_event", "country_event"]:
                return EventBlockActions
            elif node.key in ["option", "immediate"]:
                return EventOptionContext
        return EventFileActions

class GFXFileContext(ParadoxFileContext):
    @staticmethod
    def get_file_context():
        return GFXFileActions
    
    @staticmethod
    def derive_node_context(node):
        if isinstance(node, GenericBlock):
            if node.key.lower() == "spritetypes":
                return GFXFileActions
        return GenericNodeActions