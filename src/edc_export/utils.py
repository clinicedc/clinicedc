import os


def get_export_folder() -> str:
    from django.conf import settings

    if path := getattr(settings, "EDC_EXPORT_EXPORT_FOLDER", None):
        return os.path.expanduser(path)
    return os.path.join(settings.MEDIA_ROOT, "data_folder", "export")


def get_upload_folder() -> str:
    from django.conf import settings

    if path := getattr(settings, "EDC_EXPORT_UPLOAD_FOLDER", None):
        return os.path.expanduser(path)
    return os.path.join(settings.MEDIA_ROOT, "data_folder", "upload")
