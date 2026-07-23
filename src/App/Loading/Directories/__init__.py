from App.Loading.Directories.Event import EventDirectory
from App.Loading.Directories.Interface import InterfaceDirectory
from App.Loading.Directories.Loc import LocDirectory
from App.Loading.Directories.Icon import IconDirectory
from App.Loading.Directories.Character import CharacterDirectory
from App.Loading.Directories.CountryTag import CountryTagDirectory
from App.Loading.Directories.IndustrialOrganisation import MIODirectory
from App.Loading.Directories.Operations import IntelligenceOperationDirectory
from App.Loading.Directories.Raids import RaidsDirectory
from App.Loading.Directories.SpecialProjects import SpecialProjectsDirectory
from App.Loading.Directories.States import StatesDirectory

DIRECTORY_REGISTRY = {
    "events": EventDirectory,
    "interface": InterfaceDirectory,
    "localisation": LocDirectory, 
    "gfx": IconDirectory, 
    "common/characters": CharacterDirectory,
    "common/country_tags": CountryTagDirectory,
    "common/military_industrial_organization/organizations": MIODirectory,
    "common/operations": IntelligenceOperationDirectory,
    "common/raids": RaidsDirectory,
    "common/special_projects/projects":SpecialProjectsDirectory,
    "history/states": StatesDirectory
}