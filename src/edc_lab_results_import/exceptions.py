from pathlib import Path


class ResultImporterError(Exception):
    pass


class MappingsNotFoundError(Exception):
    def __init__(self, laboratory: str, path: str | Path):
        message = f"Mapping data not found for laboratory. Got {laboratory}. See {path}."
        super().__init__(message)
