from dataclasses import dataclass
from typing import Optional
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import GenericBlock, GenericKeyValue, GenericNode
from App.Enums import PropagationType, ChangeState
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
    value:Optional[GenericBlock|GenericKeyValue|GenericNode]
    state:ChangeState
    
@dataclass
class AppendNodeRequest:
    file:Optional[PDXScriptFile]
    node:GenericBlock|GenericKeyValue|GenericNode
    index:int
    value:GenericBlock|GenericKeyValue|GenericNode

