from pathlib import Path


def get_export_folder() -> Path:
    from django.conf import settings  # noqa: PLC0415

    if path := getattr(settings, "EDC_EXPORT_EXPORT_FOLDER", None):
        return Path(path).expanduser()
    return Path(settings.MEDIA_ROOT) / "data_folder" / "export"
