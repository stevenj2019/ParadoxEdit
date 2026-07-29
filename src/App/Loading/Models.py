from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.Directories.Base import GenericDirectory

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from App.Contexts.Base import ParadoxContext
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile


@dataclass(frozen=True)
class UnloadedFile:
    path: Path
    filename: str
    loader: Optional[PDXScriptFile | PDXLocFile | IconFile]

    def load(self) -> UnloadedFile | PDXScriptFile | PDXLocFile | IconFile:
        if self.loader:
            try:
                return self.loader(self.path)
            except UnicodeDecodeError:
                pass
        return self


class IconFile:
    def __init__(self, path: Path) -> None:
        self.filepath = path
        self.filename = self.filepath.name
        self.source_path = None

    def get_path(self) -> Path:
        return self.filepath if not self.source_path else self.source_path

    @classmethod
    def add(cls, save_path: Path, source_path: Path) -> IconFile:
        icon = cls(save_path)
        icon.source_path = source_path
        return icon


@dataclass(eq=False)
class FileReference:
    directory: GenericDirectory
    file: UnloadedFile | PDXScriptFile | PDXLocFile | IconFile
    context: ParadoxContext
    read_only: bool

    def commit(self, safe_mode: bool) -> None:
        match self.file:
            case PDXScriptFile() | PDXLocFile():
                if safe_mode:
                    self.file.backup_file()
                self.file.to_pdx_file()
            case IconFile():
                shutil.copyfile(self.file.source_path, self.file.filepath)
