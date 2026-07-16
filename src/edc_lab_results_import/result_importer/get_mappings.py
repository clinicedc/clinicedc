from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings

from ..exceptions import MappingsNotFoundError

__all__ = ["get_mappings"]


def get_mappings(laboratory: str) -> dict[str, dict[str, str]]:
    """Load utestid and unit mappings for this laboratory from
    a JSON file.
    """
    mappings = {}
    if getattr(settings, "EDC_LAB_RESULTS_MAPPING_FILES", None):
        path = Path(settings.EDC_LAB_RESULTS_MAPPING_FILES.get(laboratory))
        with path.open("r") as f:
            data = json.load(f)
        try:
            mappings = data[laboratory]
        except KeyError as e:
            raise MappingsNotFoundError(laboratory, path) from e
    return mappings
