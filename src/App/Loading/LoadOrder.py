from pathlib import Path
from App.Loading.ParadoxSource import ParadoxSource, ParadoxVanilla, ParadoxMod

class ParadoxLoadOrder:
    def __init__(self, vanilla_loaded):
        self.vanilla_loaded = vanilla_loaded
        self.sources:list[ParadoxSource] = []

    def load_vanilla(self, path):
        self.sources.append(ParadoxVanilla(path))
    
    def load_mod(self, path):
        self.sources.append(ParadoxMod(path))

    def resolve(self):
        self._resolve_dependencies()
        self._resolve_file_overrides()

    #TODO: This need to implement alphabetical load ordering for when dependencies arent avaiable
    def _resolve_dependencies(self):
        resolved = []
        remaining = self.sources.copy()
        source_by_name = {source.source_name:source
                          for source in self.sources}

        while remaining:
            for source in remaining:
                if isinstance(source, ParadoxVanilla):
                    resolved.insert(0, source)
                    remaining.remove(source)
                    break

                dependencies = [
                    source_by_name[name] 
                    for name in source.dependencies
                    if name in source_by_name
                ]

                if all(dependency in resolved for dependency in dependencies):
                    resolved.append(source)
                    remaining.remove(source)
                    break

        self.sources = resolved

    def _resolve_file_overrides(self):
        loaded_sources = []
        for source in self.sources:
            for target in loaded_sources:
                for path in source.replace_paths:
                    target.apply_replace_path(path)
                self._apply_override_traversal(source, source.root, target)
            loaded_sources.append(source)

    def _apply_override_traversal(self, source, source_dir, target_source):
        for file in source_dir.files.values():
            path = Path(file.file.path)
            path = path.relative_to(source.file_path)
            target_source.apply_override(path)
        for directory in source_dir.directories.values():
            self._apply_override_traversal(source, directory, target_source)

    def parse_files(self):
        for source in self.sources:
            source.parse_files()

    def token_collection(self):
        tokens = {}
        for source in self.sources:
            source_tokens = source.token_collection()

            for key, values in source_tokens.items():
                tokens.setdefault(key, set()).update(values)

        return tokens
    
    def metadata_collection(self):
        metadata = {}
        for source in self.sources:
            source_metadata = source.metadata_collection()

            for key, values in source_metadata.items():
                metadata.setdefault(key, type(values)()).update(values)

        return metadata