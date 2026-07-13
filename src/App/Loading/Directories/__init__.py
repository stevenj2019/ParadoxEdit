from App.Loading.Directories.Event import EventDirectory
from App.Loading.Directories.GFX import GFXDirectory
from App.Loading.Directories.Loc import LocDirectory

DIRECTORY_REGISTRY = {
    "events": EventDirectory,
    "interface": GFXDirectory,
    "localisation": LocDirectory
}