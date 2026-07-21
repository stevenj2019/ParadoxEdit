from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.LoadOrder import ParadoxLoadOrder
    from App.Loading.Directories.Base import GenericDirectory, ParadoxFileContext, ParadoxBlockContext, ParadoxNodeContext
    from App.Loading.Models import FileReference
    from App.Services import Workspace

from dataclasses import dataclass
from typing import Optional, Callable

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import GenericBlock, GenericKeyValue, GenericNode

from App.Contracts.Enums import PropagationType, ChangeState
@dataclass
class ModLoaderResult:
    workspace:Workspace
    load_order:ParadoxLoadOrder
    tokens:dict
    metadata:dict
    
@dataclass
class OpenFile:
    file:PDXScriptFile|PDXLocFile
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
    target:GenericDirectory|FileReference
    action:Callable

@dataclass
class FileMutationRequest:
    directory:GenericDirectory
    file:FileReference
    state:ChangeState