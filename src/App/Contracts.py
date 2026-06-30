from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Contexts.FileContexts import ParadoxFileContext

from dataclasses import dataclass
from typing import Optional, Callable
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import GenericBlock, GenericKeyValue, GenericNode
from App.Enums import PropagationType, ChangeState

@dataclass
class OpenFile:
    file:PDXScriptFile
    context:ParadoxFileContext

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
    target:GenericBlock
    value:Callable
    state:ChangeState

    @classmethod
    def add(cls, target, factory, file=None):
        return cls(
            file=file, 
            target=target, 
            value=factory, 
            state=ChangeState.ADDED
        )
    
@dataclass
class AppendNodeRequest:
    file:Optional[PDXScriptFile]
    node:GenericBlock|GenericKeyValue|GenericNode
    index:int
    value:GenericBlock|GenericKeyValue|GenericNode

# @dataclass
# class CurrentContext:
#     file:PDXScriptFile
#     category:ParadoxFileContext
#     node:Optional[GenericBlock|GenericKeyValue|GenericNode]
