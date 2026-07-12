from App.Loading.ParadoxSource import ParadoxSource, ParadoxVanilla, ParadoxMod
class ParadoxLoadOrder:
    def __init__(self):
        self.sources:list[ParadoxSource] = []

    def _load_vanilla(self):
        return NotImplementedError
    
    def load_mod(self, path):
        self.sources.append(ParadoxMod(path))

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