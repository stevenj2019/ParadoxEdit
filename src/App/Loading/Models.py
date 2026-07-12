from dataclasses import dataclass
from typing import Optional, Callable
import os

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile

@dataclass(frozen=True)
class UnloadedFile:
    path:os.PathLike
    filename:str
    loader:Optional[PDXScriptFile|PDXLocFile]

    def load(self):
        #Temporary, till i fix per-file issues
        if self.filename.split(".")[-1] not in ("dds", "png"):
            if self.loader:
                return self.loader(self.path)
        return self