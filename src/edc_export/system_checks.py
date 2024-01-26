import os

from django.core.checks import CheckMessage, Warning

from edc_export.utils import get_export_folder, get_upload_folder


def export_dir_checks(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    if not os.path.exists(get_export_folder()):
        errors.append(
            Warning(
                f"Folder does not exist. Tried {get_export_folder()}. See edc_export.",
                id="settings.EDC_EXPORT_EXPORT_FOLDER",
            )
        )

    if not os.path.exists(get_upload_folder()):
        errors.append(
            Warning(
                f"Folder does not exist. Tried {get_upload_folder()}. See edc_export.",
                id="settings.EDC_EXPORT_UPLOAD_FOLDER",
            )
        )

    return errors
