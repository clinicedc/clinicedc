from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property

from .exceptions import EdcLabResultsStorageDirError, EdcLabResultsUploadDirError

destination_subfolder_name = "source_documents"
storage_dir_attr = "EDC_LAB_RESULTS_IMPORT_STORAGE_DIR"
upload_dir_attr = "EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR"
requisition_panel_map_attr = "EDC_LAB_RESULTS_IMPORT_REQUISITION_PANEL_MAP"


class PrivateStorage(FileSystemStorage):
    """Storage for archived source documents, rooted at the storage
    folder. See `get_storage_dir`.

    Referenced by name in migrations, do not rename.
    """

    @cached_property
    def base_location(self) -> Path:
        return get_storage_dir()

    def _clear_cached_properties(self, setting: str, **kwargs) -> None:
        super()._clear_cached_properties(setting, **kwargs)
        if setting == storage_dir_attr:
            self.__dict__.pop("base_location", None)
            self.__dict__.pop("location", None)


def _get_dir(attr: str, error_cls: type[Exception]) -> Path:
    location: str | Path = getattr(settings, attr, "")
    if not location:
        raise error_cls(f"Folder not set. See settings.{attr}.")
    location: Path = Path(location).expanduser()
    if not location.is_dir():
        raise error_cls(
            f"Folder does not exist or is not a folder. Got {location}. See settings.{attr}."
        )
    return location


def get_storage_dir() -> Path:
    """Return the folder where source documents are archived.

    Managed by `SourceDocument.pdf`. Nothing else writes here and
    PDFs are never dropped here by hand. See `get_upload_dir`.
    """
    return _get_dir(storage_dir_attr, EdcLabResultsStorageDirError)


def get_upload_dir() -> Path:
    """Return the folder where result PDFs are uploaded for import.

    `ResultImporter` parses the PDFs here and copies each one into
    the storage folder. See `get_storage_dir`.
    """
    return _get_dir(upload_dir_attr, EdcLabResultsUploadDirError)


def get_panels_by_utestid(extra_panels: list | None = None) -> dict[str, list[str]]:
    """Return {utest id: [panel name, ...]} across every registered panel.

    Point of care panels are left out. A POC result is measured at the
    clinic and never travels through a laboratory, so it can never be
    the source of an imported result. Including them would make `hba1c`
    and `glucose` look ambiguous, since each is declared by both a
    venous panel and its POC counterpart, when for an imported result
    only the venous one is possible.
    """
    # imported here, `utils` is imported before the lab profiles load
    from edc_lab.site_labs import site_labs  # noqa: PLC0415

    panels = [
        panel
        for lab_profile in site_labs.lab_profiles.values()
        for panel in lab_profile.panels.values()
    ]
    panels.extend(extra_panels or [])
    panels = [panel for panel in panels if not panel.is_poc]
    mapping: dict[str, list[str]] = {}
    for panel in panels:
        for utest_id in panel.flatten_utestids():
            names = mapping.setdefault(utest_id, [])
            if panel.name not in names:
                names.append(panel.name)
    return mapping


def get_ambiguous_utestids(extra_panels: list | None = None) -> dict[str, list[str]]:
    """Return {utest id: [panel name, ...]} for utest ids on more than
    one panel.

    Nothing in an imported result says which of them it came from, so
    these cannot be resolved from the data. Reported rather than
    guessed at.

    Point of care panels are already excluded, so `hba1c` and `glucose`
    do not appear here despite each being declared by two panels.
    """
    return {
        utest_id: sorted(names)
        for utest_id, names in get_panels_by_utestid(extra_panels).items()
        if len(names) > 1
    }


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

    Point of care panels are excluded, see `get_panels_by_utestid`. A
    utest id still declared by more than one panel after that is left
    out rather than assigned to one of them or raised on. It then behaves exactly like a
    utest id in no panel at all: the result keeps an empty
    `panel_name`, `backfill_panel_name` counts it, and
    `get_df_orphan_results` shows it as `panel_unknown`. Visible, and
    for a person to decide. See `get_ambiguous_utestids`.
    """
    return {
        utest_id: names[0]
        for utest_id, names in get_panels_by_utestid(extra_panels).items()
        if len(names) == 1
    }


def get_requisition_panel_name_map() -> dict[str, str]:
    """Return {analyte panel name: requisition panel name}.

    The panel a result is reported under is not always the panel it was
    drawn under. The white cell differentials are their own analyte
    panel but are collected on the FBC requisition, so no
    `wbc_diff` requisition exists and looking one up by the analyte
    panel can only fail.

    Deployment specific, so it is read from settings rather than
    hardcoded::

        EDC_LAB_RESULTS_IMPORT_REQUISITION_PANEL_MAP = {"wbc_diff": "fbc"}

    An unlisted panel maps to itself. `Result.panel_name` keeps the
    analyte panel either way, which is the truthful description of what
    was measured.
    """
    return dict(getattr(settings, requisition_panel_map_attr, None) or {})
