from __future__ import annotations

from collections.abc import Callable
from importlib import import_module

from django.conf import settings

from ..exceptions import ResultImporterError

__all__ = ["get_parser"]


def get_parser(laboratory: str) -> Callable:
    """Return the parser callable for this laboratory."""
    parsers: dict[str, str] = getattr(settings, "EDC_LAB_RESULTS_PARSERS", {})
    dotted_path = parsers.get(laboratory)
    if not dotted_path:
        available = ", ".join(sorted(parsers.keys())) or "(none)"
        raise ResultImporterError(
            f"No parser configured for laboratory '{laboratory}'. "
            f"Available: {available}. "
            f"Check EDC_LAB_RESULTS_PARSERS in settings."
        )
    module_path, func_name = dotted_path.rsplit(".", 1)
    try:
        module = import_module(module_path)
    except ModuleNotFoundError as e:
        raise ResultImporterError(f"Cannot import parser module '{module_path}': {e}") from e
    func = getattr(module, func_name, None)
    if func is None:
        raise ResultImporterError(
            f"Parser module '{module_path}' has no attribute '{func_name}'."
        )
    return func
