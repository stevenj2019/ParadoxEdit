from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Modules.Base import GenericCategory, ParadoxFileContext, ParadoxBlockContext, ParadoxNodeContext

from dataclasses import dataclass
from typing import Optional, Callable, List

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import GenericBlock, GenericKeyValue, GenericNode

from App.Enums import PropagationType, ChangeState

@dataclass
class OpenFile:
    file:PDXScriptFile
    context:ParadoxFileContext

@dataclass
class FileContext:
    target:GenericCategory|PDXScriptFile
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
    
@dataclass
class PropagationRequest:
    type  :PropagationType
    file  :PDXScriptFile
    node  :Optional[GenericBlock|GenericKeyValue|GenericNode]
    state :ChangeState

@dataclass
class NodeMutationRequest:
    file:Optional[PDXScriptFile]
    node:GenericBlock|GenericKeyValue
    node_value:GenericNode
    value:str|int|float

@dataclass
class BlockMutationRequest:
    file:Optional[PDXScriptFile]
    parent:PDXScriptFile|GenericBlock
    index:int
    payload:Callable|GenericBlock|GenericKeyValue|GenericNode
    state:ChangeState

    @classmethod
    def add(cls, parent, index, payload, file=None):
        return cls(
            file=file, 
            parent=parent,
            index=index,
            payload=payload, 
            state=ChangeState.ADDED
        )

@dataclass
class BulkMutationRequest:
    target:GenericCategory|PDXScriptFile
    action:Callable