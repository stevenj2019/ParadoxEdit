from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Contexts.Base import ParadoxFileContext
    from App.Loading.Directories.Base import GenericDirectory
    from App.Loading.LoadOrder import ParadoxLoadOrder
    from App.Loading.Models import FileReference
    from App.Services import Workspace

from dataclasses import dataclass
from typing import Callable, Optional

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from App.Contracts.Enums import ChangeState, PropagationType, TargetProperty
from ParadoxParser import GenericBlock, GenericKeyValue, GenericNode


@dataclass
class ModLoaderResult:
    workspace: Workspace
    load_order: ParadoxLoadOrder
    # tokens: dict
    # metadata: dict


@dataclass
class OpenFile:
    file: FileReference
    context: ParadoxFileContext


@dataclass
class PropagationRequest:
    type: PropagationType
    file: FileReference
    node: Optional[GenericBlock | GenericKeyValue | GenericNode]
    state: ChangeState


@dataclass
class NodeMutationRequest:
    file: Optional[FileReference]
    node: GenericBlock | GenericKeyValue
    target: TargetProperty
    value: str | int | float


@dataclass
class BlockMutationRequest:
    file: Optional[FileReference]
    parent: FileReference | GenericBlock
    index: int
    payload: Callable | GenericBlock | GenericKeyValue | GenericNode
    state: ChangeState

    @classmethod
    def add(
        cls,
        parent: FileReference | GenericBlock,
        index: int,
        payload: Callable | GenericBlock | GenericKeyValue | GenericNode,
        file: FileReference = None,
    ) -> BlockMutationRequest:
        return cls(
            file=file,
            parent=parent,
            index=index,
            payload=payload,
            state=ChangeState.ADDED,
        )


@dataclass
class BulkMutationRequest:
    target: GenericDirectory | FileReference
    action: Callable


@dataclass
class FileMutationRequest:
    directory: GenericDirectory
    file: FileReference
    state: ChangeState


@dataclass
class InLineEditRequest:
    tree: QTreeWidget
    item: QTreeWidgetItem
    node: GenericBlock | GenericKeyValue | GenericNode
    target: TargetProperty


@dataclass
class SearchResult:
    file: FileReference
    results: list
