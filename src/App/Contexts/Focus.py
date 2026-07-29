from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference
from App.Contexts import BlockContext
from App.Contexts.Base import (
    GFXFieldContext,
    LocalisationFieldContext,
    ParadoxBlockContext,
    ParadoxContext,
    ParadoxFileContext,
    ParadoxNodeContext,
)
from App.GUI.Actions import Action, ActionsResult
from App.GUI.Forms.LocaliseKey import LocaliseFocusForm
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode


class FocusTreeContext(ParadoxContext):
    @staticmethod
    def get_file_context() -> type[ParadoxFileContext]:
        return FocusFileContext

    @staticmethod
    def get_block_context(node: GenericNode) -> type[ParadoxBlockContext]:
        if node.key == "focus":
            return FocusBlockContext
        elif node.key == "focus_tree":
            return FocusTreeBlockContext
        return ParadoxBlockContext

    @staticmethod
    def get_node_context(
        parent_node: GenericBlock, node: GenericNode
    ) -> type[ParadoxNodeContext]:
        if isinstance(node, GenericKeyValue):
            if parent_node.key == "focus" and node.key == "id":
                return LocalisationFieldContext
            elif node.key == "icon":
                return GFXFieldContext
        return ParadoxNodeContext


class FocusFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(
        app_controller: AppController, file: FileReference
    ) -> ActionsResult:
        return [*ParadoxFileContext.get_actions(app_controller, file)]


class FocusRootContext(ParadoxBlockContext):
    @staticmethod
    def get_actions(
        app_controller: AppController, block_context: BlockContext
    ) -> ActionsResult:
        return [*ParadoxNodeContext.get_actions(app_controller, block_context)]

class FocusTreeBlockContext(ParadoxBlockContext):
    @staticmethod
    def get_actions(app_controller:AppController, block_context:BlockContext) -> ActionsResult:
        return [

        ]
class FocusBlockContext(ParadoxBlockContext):
    @staticmethod
    def get_actions(app_controller:AppController, block_context:BlockContext) -> ActionsResult:
        return [
            Action("Localise Focus",
                   lambda:LocaliseFocusForm(app_controller, block_context.key_node),
                   True,
            ),
        ]