from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property

from .exceptions import EdcLabResultsPrivatePathError

destination_subfolder_name = "source_documents"
private_path_attr = "EDC_LAB_RESULTS_IMPORT_PRIVATE_PATH"


class PrivateStorage(FileSystemStorage):
    @cached_property
    def base_location(self) -> Path:
        return get_private_path()

    def _clear_cached_properties(self, setting: str, **kwargs) -> None:
        super()._clear_cached_properties(setting, **kwargs)
        if setting == private_path_attr:
            self.__dict__.pop("base_location", None)
            self.__dict__.pop("location", None)


def get_private_path() -> Path:
    location: str | Path = getattr(settings, private_path_attr, "")
    if not location:
        raise EdcLabResultsPrivatePathError(
            f"Private path not set. See settings.{private_path_attr}."
        )
    location: Path = Path(location).expanduser()
    if not location.is_dir():
        raise EdcLabResultsPrivatePathError(
            f"Private path does not exist or is not a folder. Got {location}. "
            f"See settings.{private_path_attr}."
        )
    return location
