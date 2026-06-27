from dataclasses import dataclass
from typing import Optional
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import GenericBlock, GenericKeyValue, GenericNode
from App.Enums import PropagationType, ChangeState, SaveTarget, ExpansionMode

@dataclass
class PropagationRequest:
    type  :PropagationType
    file  :PDXScriptFile
    node  :Optional[GenericBlock|GenericKeyValue|GenericNode]
    state :ChangeState

@dataclass
class ModifyNodeRequest:
    file:Optional[PDXScriptFile]
    node:GenericBlock|GenericKeyValue|GenericNode
    value:str|int|float

@dataclass
class AppendNodeRequest:
    file:Optional[PDXScriptFile]
    node:GenericBlock|GenericKeyValue|GenericNode
    index:int
    value:GenericBlock|GenericKeyValue|GenericNode

@dataclass
class RemoveNodeRequest:
    file:Optional[PDXScriptFile]
    node:GenericBlock|GenericKeyValue|GenericNode

# class ModifyStructureRequest:TODO

@dataclass
class SaveRequest:
    type:SaveTarget #This is an Enum .ALL, .OPEN

@dataclass
class ExpansionRequest:
    mode:ExpansionMode #TThis is an Enum .ALL, .DEPTH, .FROM_NODE
    depth:int
    from_node: #unsure of type, i am almost certain QTreeWidgetItem