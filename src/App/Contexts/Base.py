from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference

from App.Contexts import BlockContext, NodeContext
from App.Contracts import BulkMutationRequest
from App.Enums import PDXMetadata
from App.GUI.Actions import Action, ActionsResult

# from App.PDXFactory.Blocks.Generic import comment_node
from App.Scripts.Generic import clear_comments, clear_whitespace
from ParadoxParser.ParadoxNodes import GenericBlock, GenericNode


def dummy() -> None:
    pass


class ParadoxContext:
    @staticmethod
    def get_file_context() -> type[ParadoxFileContext]:
        return ParadoxFileContext

    @staticmethod
    def get_block_context(node: GenericNode) -> type[ParadoxBlockContext]:
        return ParadoxBlockContext

    @staticmethod
    def get_node_context(
        parent_node: GenericBlock, node: GenericNode
    ) -> type[ParadoxNodeContext]:
        return ParadoxNodeContext


class ParadoxFileContext:
    @staticmethod
    def get_actions(
        app_controller: AppController, file: FileReference
    ) -> ActionsResult:
        return [
            Action(
                "Remove Comments",
                lambda: app_controller.request_bulk_mutation.emit(
                    BulkMutationRequest(target=file, action=clear_comments)
                ),
                True,
            ),
            Action(
                "Reformat File",
                lambda: app_controller.request_bulk_mutation.emit(
                    BulkMutationRequest(target=file, action=clear_whitespace)
                ),
                True,
            ),
        ]


class ParadoxBlockContext:
    @staticmethod
    def get_actions(
        app_controller: AppController, block_context: BlockContext
    ) -> ActionsResult:
        return

    def errors(app_controller: AppController, node_context: NodeContext) -> str:
        return


class ParadoxNodeContext:
    @staticmethod
    def get_actions(
        app_controller: AppController, block_context: BlockContext
    ) -> ActionsResult:
        return [
            #     Action(
            #         "Add Comment",
            #         lambda: app_controller.request_block_mutation.emit(
            #             BlockMutationRequest.add(
            #                 block_context.parent, block_context.parent_index, comment_node
            #             )
            #         ),
            #         True,
            #     )
        ]

    def errors(app_controller: AppController, node_context: NodeContext) -> str:
        return


class ReadOnlyContext(ParadoxContext):
    @staticmethod
    def get_file_context() -> type[VanillaFileContext]:
        return VanillaFileContext

    @staticmethod
    def get_block_context(node: GenericNode) -> type[NullContext]:
        return NullContext

    @staticmethod
    def get_node_context(
        parent_node: GenericBlock, node: GenericNode
    ) -> type[NullContext]:
        return NullContext


class VanillaFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(
        app_controller: AppController, file: FileReference
    ) -> ActionsResult:
        from App.GUI.Forms.CopyFile import CopyFileForm
        return [
            Action("Copy File to source...",
                   lambda:CopyFileForm(app_controller, file),
                   True)
        ]

    def errors(app_controller: AppController, node_context: NodeContext) -> str:
        return

class NullContext:
    @staticmethod
    def get_actions(
        app_controller: AppController, block_context: BlockContext
    ) -> ActionsResult:
        return [Action("No Actions Available", dummy, False)]
    
    def errors(app_controller: AppController, node: GenericNode) -> str|None:
        return None
    
class LocalisationFieldContext:
    @staticmethod
    def get_actions(
        app_controller: AppController, node_context: NodeContext
    ) -> ActionsResult:
        from App.GUI.Forms.LocaliseKey import LocaliseNodeForm

        return [
            Action(
                "Localise",
                lambda: LocaliseNodeForm(app_controller, node_context.key_node),
                True,
            )
        ]

    def errors(app_controller: AppController, node: GenericNode) -> str:
        if (
            node.value
            not in app_controller.registry.get_metadata(PDXMetadata.LocKey).keys()
        ):
            return "Localisation does not exist"


class GFXFieldContext:
    @staticmethod
    def get_actions(
        app_controller: AppController, node_context: NodeContext
    ) -> ActionsResult:
        return [
            Action(
                "Preview Icon",
                lambda: app_controller.main.request_icon_preview.emit(
                    node_context.key_node.value.value
                ),
                True,
            )
        ]

    def errors(app_controller: AppController, node: GenericNode) -> str:
        if (
            node.value
            not in app_controller.registry.get_metadata(PDXMetadata.GFXIcon).keys()
        ):
            return "Icon does not exist"
        else:
            return
