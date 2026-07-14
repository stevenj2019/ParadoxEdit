from App.Loading.Directories.Event import EventDirectory
from App.Loading.Directories.Interface import InterfaceDirectory
from App.Loading.Directories.Loc import LocDirectory

DIRECTORY_REGISTRY = {
    "events": EventDirectory,
    "interface": InterfaceDirectory,
    "localisation": LocDirectory
}