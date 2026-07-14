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

@dataclass
class FileReference:
    file:UnloadedFile|PDXScriptFile|PDXLocFile
    context:ParadoxContext
    read_only:bool