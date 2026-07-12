from App.Loading.Directories.Event import EventDirectoryContext
from App.Loading.Directories.GFX import GFXDirectoryContext
from App.Loading.Directories.Loc import LocDirectoryContext

DIRECTORY_REGISTRY = {
    "events": EventDirectoryContext,
    "interface": GFXDirectoryContext,
    "localisation": LocDirectoryContext
}