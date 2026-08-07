from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Contexts.Base import (
        ParadoxBlockContext,
        ParadoxFileContext,
        ParadoxNodeContext,
    )
    from App.Loading.Directories.Base import GenericDirectory
    from App.Loading.ParadoxSource import ParadoxSource
from dataclasses import dataclass

from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode


@dataclass
class FileContext:
    target: ParadoxSource | GenericDirectory | PDXScriptFile | PDXLocFile
    context: ParadoxFileContext


@dataclass
class BlockContext:
    parent: GenericBlock
    parent_index: int
    parent_context: ParadoxBlockContext


@dataclass
class NodeContext:
    key_node: GenericBlock | GenericKeyValue
    selected_node: GenericNode
    node_context: ParadoxNodeContext
