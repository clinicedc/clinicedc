from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property

from .exceptions import EdcLabResultsPrivatePathError, EdcLabResultsUtestidError

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


def get_panel_name_by_utestid(
    extra_panels: list | None = None,
) -> dict[str, str]:
    """Return {utest id: panel name} across every registered panel.

    The single source of the mapping. `ResultImporter.df_utestid` builds
    its dataframe from this, and `backfill_panel_name` repairs rows the
    importer saved before it wrote `panel_name` at all, so the two
    cannot drift.

    `extra_panels` covers a panel that no lab profile registers but that
    results are nonetheless reported against, `wbc_differential` being
    the one in practice.

    Raises where one utest id maps to two panels, which would make the
    panel of a result ambiguous.
    """
    # imported here, `utils` is imported before the lab profiles load
    from edc_lab.site_labs import site_labs  # noqa: PLC0415

    mapping: dict[str, str] = {}
    panels = [
        panel
        for lab_profile in site_labs.lab_profiles.values()
        for panel in lab_profile.panels.values()
    ]
    panels.extend(extra_panels or [])
    for panel in panels:
        for utest_id in panel.flatten_utestids():
            if mapping.get(utest_id, panel.name) != panel.name:
                raise EdcLabResultsUtestidError(
                    "More than one panel declares this utest id. "
                    f"Got '{utest_id}' on '{mapping[utest_id]}' and '{panel.name}'."
                )
            mapping.update({utest_id: panel.name})
    return mapping
