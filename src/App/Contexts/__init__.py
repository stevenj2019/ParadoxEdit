from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Contexts.Base import (GenericDirectory, ParadoxFileContext, 
                                   ParadoxBlockContext, ParadoxNodeContext)
    
from dataclasses import dataclass

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode

@dataclass
class FileContext:
    target:GenericDirectory|PDXScriptFile|PDXLocFile
    context:ParadoxFileContext

@dataclass
class BlockContext:
    parent:GenericBlock
    parent_index:int
    parent_context:ParadoxBlockContext

@dataclass
class NodeContext:
    node:GenericBlock|GenericKeyValue|GenericNode
    node_context:ParadoxNodeContext
