from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference

from App.Contexts.Base import (
    ParadoxBlockContext,
    ParadoxContext,
    ParadoxFileContext,
    ParadoxNodeContext,
)
from App.Contracts import BulkMutationRequest
from App.GUI.Actions import Action, ActionsResult
from App.Scripts.Localisation import convert_legacy
from ParadoxParser.ParadoxNodes import GenericBlock, GenericNode


class LocalisationContext(ParadoxContext):
    @staticmethod
    def get_file_context() -> type[ParadoxFileContext]:
        return LocalisationFileContext

    @staticmethod
    def get_block_context(node: GenericNode) -> type[ParadoxBlockContext]:
        return ParadoxNodeContext

    @staticmethod
    def get_node_context(
        parent_node: GenericBlock, node: GenericNode
    ) -> type[ParadoxNodeContext]:
        return ParadoxNodeContext


class LocalisationFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(
        app_controller: AppController, file: FileReference
    ) -> ActionsResult:
        return [
            *ParadoxFileContext.get_actions(app_controller, file),
            Action(
                "Convert to new format",
                lambda: app_controller.request_bulk_mutation.emit(
                    BulkMutationRequest(target=file, action=convert_legacy)
                ),
                True,
            ),
        ]
