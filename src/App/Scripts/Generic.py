from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference

from App.Contracts.Enums import ChangeState
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment, GenericNode


def clear_comments(file: FileReference, app_controller: AppController) -> None:
    def tombstone_comments(node: GenericNode) -> None:
        if isinstance(node, GenericBlock):
            for child in node.nodes:
                tombstone_comments(child)
        if isinstance(node, GenericComment):
            app_controller.file_system.changed_file(file, node, ChangeState.DELETED)

    for node in file.nodes:
        tombstone_comments(node)


def clear_whitespace(file: FileReference, app_controller: AppController) -> None:
    app_controller.file_system.change_tracker.set_file_state(file, ChangeState.MODIFIED)
