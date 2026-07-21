from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.Directories.Base import GenericDirectory

from dataclasses import dataclass
from typing import Optional, Callable
import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile

from App.Contexts.Base import ParadoxContext

@dataclass(frozen=True)
class UnloadedFile:
    path:Path
    filename:str
    loader:Optional[PDXScriptFile|PDXLocFile]

    def load(self):
        if self.loader:
            try:
                return self.loader(self.path)
            except UnicodeDecodeError:
                pass
        return self

class IconFile:
    def __init__(self, path:Path):
        self.filepath = path
        self.filename = self.filepath.name

@dataclass
class FileReference:
    directory:GenericDirectory
    file:UnloadedFile|PDXScriptFile|PDXLocFile|IconFile
    context:ParadoxContext
    read_only:bool