from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference


from App.Contexts import BlockContext
from App.Contexts.Base import (
    ParadoxBlockContext,
    ParadoxContext,
    ParadoxFileContext,
    ParadoxNodeContext,
)
from App.GUI.Actions import Action, ActionsResult
from App.GUI.Forms.AddGFX import AddNewGFXForm

# from App.PDXFactory.Blocks.Sprites import GFX_icon, GFX_shine_icon
from ParadoxParser.ParadoxNodes import GenericBlock, GenericNode


class GFXContext(ParadoxContext):
    @staticmethod
    def get_file_context() -> type[ParadoxFileContext]:
        return GFXFileContext

    @staticmethod
    def get_block_context(node: GenericNode) -> type[ParadoxBlockContext]:
        if isinstance(node, GenericBlock):
            if node.key.lower() == "spritetypes":
                return GFXSpriteTypesContext
        return GFXRootContext

    @staticmethod
    def get_node_context(
        parent_node: GenericBlock, node: GenericNode
    ) -> type[ParadoxNodeContext]:
        return ParadoxNodeContext


class GFXFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(
        app_controller: AppController, file: FileReference
    ) -> ActionsResult:
        # from App.GUI.Forms.AddGFX import AddNewGFXForm
        return [
            *ParadoxFileContext.get_actions(app_controller, file),
            Action("Bulk-Upload Sprites",
                   lambda:AddNewGFXForm(app_controller, file),
                   True)
        ]


class GFXRootContext(ParadoxBlockContext):
    @staticmethod
    def get_actions(
        app_controller: AppController, block_context: BlockContext
    ) -> ActionsResult:
        return [*ParadoxNodeContext.get_actions(app_controller, block_context)]


class GFXSpriteTypesContext(ParadoxBlockContext):
    def get_actions(
        app_controller: AppController, block_context: BlockContext
    ) -> ActionsResult:
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            # Action(
            #     "Add Static Sprite",
            #     lambda: app_controller.request_block_mutation.emit(
            #         BlockMutationRequest.add(
            #             block_context.parent, block_context.parent_index, GFX_icon
            #         )
            #     ),
            #     True,
            # ),
            # Action(
            #     "Add Focus _shine Sprite",
            #     lambda: app_controller.request_block_mutation.emit(
            #         BlockMutationRequest.add(
            #             block_context.parent, block_context.parent_index, GFX_shine_icon
            #         )
            #     ),
            #     True,
            # ),
        ]
