from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.utils.html import format_html
from edc_protocol.research_protocol_config import ResearchProtocolConfig

from .constants import EXPORT_PII
from .exceptions import ExporterExportFolder
from .files_emailer import FilesEmailer, FilesEmailerError
from .models_to_file import ModelsToFile


def get_export_folder() -> Path:
    if path := getattr(settings, "EDC_EXPORT_EXPORT_FOLDER", None):
        return Path(path).expanduser()
    return Path(settings.MEDIA_ROOT) / "data_folder" / "export"


def get_base_dir() -> Path:
    """Returns the base_dir used by, for example,
    shutil.make_archive.

    This is the short protocol name in lower case
    """
    base_dir: str = ResearchProtocolConfig().protocol_lower_name
    if len(base_dir) > 25:
        raise ExporterExportFolder(
            f"Invalid basedir, too long. Using `protocol_lower_name`. Got `{base_dir}`."
        )
    if not re.match(r"^[a-z0-9]+(?:_[a-z0-9]+)*$", base_dir):
        raise ExporterExportFolder(
            "Invalid base_dir, invalid characters. Using `protocol_lower_name`. "
            f"Got `{base_dir}`."
        )
    return Path(base_dir)


def get_upload_folder() -> Path:
    if path := getattr(settings, "EDC_EXPORT_UPLOAD_FOLDER", None):
        return Path(path).expanduser()
    return Path(settings.MEDIA_ROOT) / "data_folder" / "upload"


def get_export_pii_users() -> list[str]:
    return getattr(settings, "EDC_EXPORT_EXPORT_PII_USERS", [])


def raise_if_prohibited_from_export_pii_group(username: str, groups: Iterable) -> None:
    """A user form validation to prevent adding an unlisted
    user to the EXPORT_PII group.

    See also edc_auth's UserForm.
    """
    if EXPORT_PII in [grp.name for grp in groups] and username not in get_export_pii_users():
        raise forms.ValidationError(
            {
                "groups": format_html(
                    "This user is not allowed to export PII data. You may not add "
                    "this user to the <U>{text}</U> group.",
                    text="EXPORT_PII",
                )
            }
        )


def email_files_to_user(request, models_to_file: ModelsToFile) -> None:
    try:
        FilesEmailer(
            path_to_files=models_to_file.tmp_folder,
            user=request.user,
            file_ext=".zip",
            export_filenames=models_to_file.exported_filenames,
        )
    except (FilesEmailerError, ConnectionRefusedError) as e:
        messages.error(request, f"Failed to send files by email. Got '{e}'")
    else:
        messages.success(
            request,
            (
                f"Your data request has been sent to {request.user.email}. "
                "Please check your email."
            ),
        )


def update_data_request_history(request, models_to_file: ModelsToFile):
    summary = [str(x) for x in models_to_file.exported_filenames]
    summary.sort()
    data_request_model_cls = django_apps.get_model("edc_export.datarequest")
    data_request_history_model_cls = django_apps.get_model("edc_export.datarequesthistory")
    data_request = data_request_model_cls.objects.create(
        name=f"Data request {timezone.now().strftime('%Y%m%d%H%M')}",
        models="\n".join(models_to_file.models),
        user_created=request.user.username,
        site=request.site,
    )
    data_request_history_model_cls.objects.create(
        data_request=data_request,
        exported_datetime=timezone.now(),
        summary="\n".join(summary),
        user_created=request.user.username,
        user_modified=request.user.username,
        archive_filename=models_to_file.archive_filename or "",
        emailed_to=models_to_file.emailed_to,
        emailed_datetime=models_to_file.emailed_datetime,
        site=request.site,
    )
