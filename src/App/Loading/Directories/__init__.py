from App.Loading.Directories.Event import EventDirectory
from App.Loading.Directories.Interface import InterfaceDirectory
from App.Loading.Directories.Loc import LocDirectory
from App.Loading.Directories.Icon import IconDirectory

DIRECTORY_REGISTRY = {
    "events": EventDirectory,
    "interface": InterfaceDirectory,
    "localisation": LocDirectory, 
    "gfx": IconDirectory
}