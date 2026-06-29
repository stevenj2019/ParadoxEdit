#Do Not Delete these imports, solves circular imports/"Not Defined" errors
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Contracts import CurrentContext

class ParadoxFileContext:
    @staticmethod
    def file_actions(ctx:CurrentContext):
        return []
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return []

class EventFileContext(ParadoxFileContext):
    @staticmethod
    def file_actions():
        return []
    @staticmethod
    def node_actions():
        return []

class GFXFileContext(ParadoxFileContext):
    @staticmethod
    def file_actions(ctx:CurrentContext):
        return []
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return []