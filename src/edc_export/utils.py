from __future__ import annotations

import getpass
import re
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import CommandError
from django.utils import timezone
from django.utils.html import format_html

from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites

from .constants import EXPORT, EXPORT_PII
from .exceptions import ExporterExportFolder
from .files_emailer import FilesEmailer, FilesEmailerError
from .models_to_file import ModelsToFile

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import User


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


def get_export_user() -> User | AbstractBaseUser:
    username = input("Username:")
    passwd = getpass.getpass("Password for " + username + ":")
    try:
        user = get_user_model().objects.get(
            username=username, is_superuser=False, is_active=True
        )
    except ObjectDoesNotExist as e:
        raise CommandError("Invalid username or password.") from e
    if not user.check_password(passwd):
        raise CommandError("Invalid username or password.")
    return user


def validate_user_perms_or_raise(user: User, decrypt: bool | None) -> None:
    if not user.groups.filter(name=EXPORT).exists():
        raise CommandError("You are not authorized to export data.")
    if decrypt and not user.groups.filter(name="EXPORT_PII").exists():
        raise CommandError("You are not authorized to export sensitive data.")


def get_default_models_for_export(trial_prefix: str) -> list[str]:
    apps = [
        f"{trial_prefix}_consent",
        f"{trial_prefix}_lists",
        f"{trial_prefix}_subject",
        f"{trial_prefix}_ae",
        f"{trial_prefix}_prn",
        f"{trial_prefix}_screening",
    ]
    model_names = [
        "edc_appointment.appointment",
        "edc_data_manager.datadictionary",
        "edc_metadata.crfmetadata",
        "edc_metadata.requisitionmetadata",
        "edc_registration.registeredsubject",
        "edc_visit_schedule.subjectschedulehistory",
    ]

    # prepare a list of model names in label lower format
    for app_config in django_apps.get_app_configs():
        if app_config.name.startswith(trial_prefix) and app_config.name in apps:
            model_names.extend(
                [
                    model_cls._meta.label_lower
                    for model_cls in app_config.get_models()
                    if "historical" not in model_cls._meta.label_lower
                    and not model_cls._meta.proxy
                ]
            )
    return model_names


def get_model_names_for_export(
    app_labels: list[str] | None,
    model_names: list[str] | None,
) -> list[str]:
    """Returns a unique list of label_lower"""
    model_names = model_names or []
    if app_labels:
        for app_label in app_labels:
            app_config = django_apps.get_app_config(app_label)
            model_names.extend([cls._meta.label_lower for cls in app_config.get_models()])
    return list(set(model_names))


def get_site_ids_for_export(
    site_ids: list[int] | None,
    countries: list[str] | None,
) -> list[int]:
    """Returns a list of site ids"""
    if countries and site_ids:
        raise CommandError("Invalid. Specify `site_ids` or `countries`, not both.")
    for site_id in site_ids or []:
        try:
            obj = django_apps.get_model("sites.site").objects.get(id=int(site_id))
        except ObjectDoesNotExist as e:
            raise CommandError(f"Invalid site_id. Got `{site_id}`.") from e
        else:
            site_ids.append(obj.id)
    for country in countries or []:
        site_ids.extend(list(site_sites.get_by_country(country)))
    return site_ids
