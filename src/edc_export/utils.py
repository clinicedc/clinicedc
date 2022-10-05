import os


def get_export_folder() -> str:
    from django.conf import settings

    return getattr(
        settings,
        "EDC_EXPORT_EXPORT_FOLDER",
        os.path.join(settings.MEDIA_ROOT, "data_folder", "export"),
    )


def get_upload_folder() -> str:
    from django.conf import settings

    return getattr(
        settings,
        "EDC_EXPORT_UPLOAD_FOLDER",
        os.path.join(settings.MEDIA_ROOT, "data_folder", "upload"),
    )
