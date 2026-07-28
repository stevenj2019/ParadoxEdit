from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode

from App.Contexts import BlockContext
from App.Contexts.Base import (
    GFXFieldContext,
    LocalisationFieldContext,
    ParadoxBlockContext,
    ParadoxContext,
    ParadoxFileContext,
    ParadoxNodeContext,
)
from App.PDXFactory.Blocks.Events import (
    add_namespace_keyval,
    country_event_block,
    immediate_block,
    news_event_block,
    option_block,
)


class FocusTreeContext(ParadoxContext):
    @staticmethod
    def get_file_context() -> type[ParadoxFileContext]:
        return FocusFileContext
    
    @staticmethod
    def get_block_context(node:GenericNode) -> type[ParadoxBlockContext]:
        return FocusRootContext
    
    @staticmethod
    def get_node_context(parent_node:GenericBlock, node:GenericNode) -> type[ParadoxNodeContext]:
        if isinstance(node, GenericKeyValue):
            if parent_node.key == "focus" and node.key == "id":
                return LocalisationFieldContext
            elif node.key == "icon":
                return GFXFieldContext
        return ParadoxNodeContext
            
class FocusFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller:AppController, file:FileReference):
        return [
            *ParadoxFileContext.get_actions(app_controller, file)
        ]

class FocusRootContext(ParadoxBlockContext):
    @staticmethod
    def get_actions(app_controller:AppController, block_context:BlockContext):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context)
        ]
