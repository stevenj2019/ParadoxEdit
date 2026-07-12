from dataclasses import dataclass
from typing import Optional, Callable
import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile

@dataclass(frozen=True)
class UnloadedFile:
    path:Path
    filename:str
    loader:Optional[PDXScriptFile|PDXLocFile]

    def load(self):
        #Temporary, till i fix per-file issues
        # if self.filename.split(".")[-1] not in ("dds", "png"):
        if self.loader:
            try:
                return self.loader(self.path)
            except UnicodeDecodeError:
                pass
        return self