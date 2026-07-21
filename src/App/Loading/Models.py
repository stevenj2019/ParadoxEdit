from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.Directories.Base import GenericDirectory

import shutil
from dataclasses import dataclass
from typing import Optional
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
        self.source_path = None

    def get_path(self):
        return self.filepath if not self.source_path else self.source_path
    
    @classmethod
    def add(cls, save_path, source_path):
        icon = cls(save_path)
        icon.source_path = source_path
        return icon

@dataclass(eq=False)
class FileReference:
    directory:GenericDirectory
    file:UnloadedFile|PDXScriptFile|PDXLocFile|IconFile
    context:ParadoxContext
    read_only:bool

    def commit(self, safe_mode):
        match self.file:
            case PDXScriptFile()|PDXLocFile():
                if safe_mode:
                    self.file.backup_file()
                self.file.to_pdx_file()
            case IconFile():
                shutil.copyfile(self.file.source_path, self.file.filepath)