from pathlib import Path

from App.Loading.Directories.Base import GenericDirectory
from App.Loading.ParadoxSource import ParadoxMod, ParadoxSource, ParadoxVanilla


class ParadoxLoadOrder:
    def __init__(self, vanilla_loaded: bool) -> None:
        self.vanilla_loaded = vanilla_loaded
        self.sources: list[ParadoxSource] = []

    def load_vanilla(self, path: Path) -> None:
        self.sources.append(ParadoxVanilla(path))

    def load_mod(self, path: Path) -> None:
        self.sources.append(ParadoxMod(path))

    def resolve(self) -> None:
        # self._resolve_dependencies()
        dependency_graph = self._build_dependency_graph()
        self.sources = self._resolve_load_order(dependency_graph)
        self._resolve_file_overrides()
        self._clear_empty_directories()

    def _build_dependency_graph(self) -> dict[ParadoxSource, str]:
        source_by_name = {source.source_name: source for source in self.sources}

        graph = {}

        for source in self.sources:
            if not isinstance(source, ParadoxVanilla):
                graph[source] = [
                    source_by_name[name]
                    for name in source.dependencies
                    if name in source_by_name
                ]

        return graph

    def _resolve_load_order(
        self, graph: dict[ParadoxSource, str]
    ) -> list[ParadoxSource]:
        resolved = list()
        vanilla = next(
            (source for source in self.sources if isinstance(source, ParadoxVanilla)),
            None,
        )
        if vanilla:
            resolved.append(vanilla)

        remaining = set(graph.keys())

        while remaining:
            available = [
                source
                for source in remaining
                if all(dependency in resolved for dependency in graph[source])
            ]

            if not available:
                # circular dependency / impossible order
                raise Exception("Unable to resolve load order")

            available.sort(key=lambda source: source.source_name.lower())

            source = available[0]

            resolved.append(source)
            remaining.remove(source)

        return resolved

    def _resolve_file_overrides(self) -> None:
        loaded_sources = []
        for source in self.sources:
            for target in loaded_sources:
                for path in source.replace_paths:
                    target.apply_replace_path(path)
                self._apply_override_traversal(source, source.root, target)
            loaded_sources.append(source)

    def _apply_override_traversal(
        self,
        source: ParadoxSource,
        source_dir: GenericDirectory,
        target_source: ParadoxSource,
    ) -> None:
        for file in source_dir.files.values():
            path = Path(file.file.path)
            path = path.relative_to(source.file_path)
            target_source.apply_override(path)
        for directory in source_dir.directories.values():
            self._apply_override_traversal(source, directory, target_source)

    def _clear_empty_directories(self) -> None:
        for source in self.sources:
            source.root.prune()
