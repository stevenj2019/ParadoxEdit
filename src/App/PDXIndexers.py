import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode, GenericString

from App.Enums import PDXTokens
from App.Services import AppLogger

def get_scope_indices(base_path:os.PathLike, file_path:os.PathLike):
    data = {}
    INDEXERS = {
        PDXTokens.CHARACTER: CharacterTokenIndexer,
        PDXTokens.COUNTRY: CountryTagIndexer,
        PDXTokens.ORGANISATION: IndustrialOrganisationIndexer,
        PDXTokens.OPERATION: OperationsIndexer,
        PDXTokens.CONTRACTS: ContractIndexer,
        PDXTokens.RAID: RaidIndexer,
        PDXTokens.SPECIAL_PROJECT: SpecialProjectIndexer,
        PDXTokens.STATE: StateIndexer,
        PDXTokens.STRATEGIC_REGION:StrategicRegionIndexer,
    }
    for key, cls in INDEXERS.items():
        indexer = cls(base_path, file_path)
        data[key] = indexer.get_tokens()
    return data

class GenericIndexer:
    def __init__(self, base:os.PathLike, mod:os.PathLike, paths:list[os.PathLike]):
        self.file_paths:dict[os.PathLike, os.PathLike] = {}
        self.files:list[PDXScriptFile] = []
        self.tokens:set[str] = set()
        for path in paths:
            self._read_directory(base, path)
            self._read_directory(mod, path)

        self.parse_files()
        try:
            self._tokenise()
        except NotImplementedError:
            pass

    def _read_directory(self, base_path, relative_path):
        path = Path(os.path.join(base_path, relative_path))
        if not path.exists():
            return
        for root, dirs, files in os.walk(path):
            for name in files:
                full_path = Path(os.path.join(root, name))
                path_key = full_path.relative_to(base_path)
                self.file_paths[path_key] = full_path
    
    def parse_files(self):
        for path in self.file_paths.values():
            try:
                file = PDXScriptFile(path)
                self.files.append(file)
                AppLogger.info(f"loaded {path.name}")
            except Exception as e:
                AppLogger.error(f"loading of {path.name} failed.")
                AppLogger.exception(e)
                

    def _tokenise(self):
        return NotImplementedError
    
    def get_tokens(self):
        return self.tokens
    
class CharacterTokenIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["common/characters"])

    def _tokenise(self):
        for file in self.files:
            characters_blocks = [block for block in file.nodes if isinstance(block, GenericBlock) and block.key.lower()=="characters"]
            for block in characters_blocks:
                for node in block.nodes:
                    if isinstance(node, GenericBlock):
                        self.tokens.add(node.key)

class CountryTagIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["common/country_tags"])

    def _tokenise(self):
        for file in self.files:
            for node in file.nodes:
                if isinstance(node, GenericKeyValue):
                    value_node = node.value
                    if isinstance(value_node, GenericString):
                        self.tokens.add(node.key)

class IndustrialOrganisationIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["common/military_industrial_organization/organizations"]) #"organization" lol

    def _tokenise(self):
        for file in self.files:
            for block in file.nodes:
                if isinstance(block, GenericBlock):
                    self.tokens.add(block.key)

class OperationsIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["common/operations"])

    def _tokenise(self):
        for file in self.files:
            for block in file.nodes:
                if isinstance(block, GenericBlock):
                    self.tokens.add(block.key)

class ContractIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["common/operations"])

class RaidIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["common/raids"])

    def _tokenise(self):
        for file in self.files:
            types_blocks = [block for block in file.nodes if isinstance(block, GenericBlock) and block.key.lower()=="types"]
            for block in types_blocks:
                for node in block.nodes:
                    if isinstance(node, GenericBlock):
                        self.tokens.add(node.key)

class SpecialProjectIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["common/special_projects/projects"])

    def _tokenise(self):
        for file in self.files:
            for block in file.nodes:
                if isinstance(block, GenericBlock):
                    self.tokens.add(block.key)

#Unsure about these
class StateIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["history/states"])

    def _tokenise(self):
        for file in self.files:
            state_blocks = [block for block in file.nodes if isinstance(block, GenericBlock) and block.key.lower()=="state"]
            for block in state_blocks:
                id_keyval = next((node for node in block.nodes if isinstance(node, GenericKeyValue) and node.key.lower() == "id"), None)
                if id_keyval:
                    self.tokens.add(str(id_keyval.value.value))

class StrategicRegionIndexer(GenericIndexer):
    def __init__(self, base_path:os.PathLike, file_path:os.PathLike):
        super().__init__(base_path, file_path, ["map/strategicregions"])
