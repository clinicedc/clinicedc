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
                    text=EXPORT_PII,
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


def record_cli_export_audit(
    user: User | AbstractBaseUser,
    models_to_file: ModelsToFile,
    *,
    decrypt: bool,
    export_format: str | int,
    site_ids: list[int] | None = None,
    countries: list[str] | None = None,
    trial_prefix: str | None = None,
    include_historical: bool = False,
    export_path: Path | str | None = None,
) -> tuple:
    """Record a CLI-initiated export to DataRequest / DataRequestHistory.

    Web-initiated exports record history via `update_data_request_history`.
    CLI exports have no `request` object, so the management command calls
    this helper to leave an equivalent audit trail: who ran the export,
    what models, with what filters, decrypted or not, where it landed.

    The `site` FK is left null; `SiteModelMixin.get_site_on_create` will
    assign from `settings.SITE_ID` at save-time, matching how other
    CLI-created rows behave.

    Returns the (data_request, data_request_history) instances (primarily
    for tests).
    """
    summary = sorted(str(x) for x in (models_to_file.exported_filenames or []))
    data_request_model_cls = django_apps.get_model("edc_export.datarequest")
    data_request_history_model_cls = django_apps.get_model("edc_export.datarequesthistory")

    description_lines = [
        "Initiated via `export_models` management command.",
        f"export_format={export_format}",
        f"decrypt={bool(decrypt)}",
        f"include_historical={bool(include_historical)}",
    ]
    if trial_prefix:
        description_lines.append(f"trial_prefix={trial_prefix}")
    if site_ids:
        description_lines.append(f"site_ids={','.join(str(s) for s in site_ids)}")
    if countries:
        description_lines.append(f"countries={','.join(countries)}")
    if export_path is not None:
        description_lines.append(f"export_path={export_path}")

    data_request = data_request_model_cls.objects.create(
        name=f"CLI export {timezone.now().strftime('%Y%m%d%H%M')}",
        description="\n".join(description_lines),
        decrypt=bool(decrypt),
        export_format=str(export_format),
        models="\n".join(models_to_file.models or []),
        user_created=user.username,
    )
    data_request_history = data_request_history_model_cls.objects.create(
        data_request=data_request,
        exported_datetime=timezone.now(),
        summary="\n".join(summary),
        user_created=user.username,
        user_modified=user.username,
        archive_filename=models_to_file.archive_filename or "",
    )
    return data_request, data_request_history


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
    if decrypt and not user.groups.filter(name=EXPORT_PII).exists():
        raise CommandError("You are not authorized to export sensitive data.")


def get_default_models_for_export(trial_prefix: str) -> list[str]:
    """Return default model list for a trial identified by `trial_prefix`.

    Raises CommandError if no installed apps match the trial_prefix —
    likely a typo, otherwise the caller would silently get only the six
    generic framework models below and think they exported the trial.
    """
    expected_apps = [
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
    matched: list[str] = []
    for app_config in django_apps.get_app_configs():
        if app_config.name.startswith(trial_prefix) and app_config.name in expected_apps:
            matched.append(app_config.name)
            model_names.extend(
                [
                    model_cls._meta.label_lower
                    for model_cls in app_config.get_models()
                    if "historical" not in model_cls._meta.label_lower
                    and not model_cls._meta.proxy
                ]
            )

    if not matched:
        raise CommandError(
            f"Unknown trial_prefix `{trial_prefix}`. No installed app matched. "
            f"Expected at least one of: {', '.join(expected_apps)}."
        )
    return model_names


def get_model_names_for_export(
    app_labels: list[str] | None,
    model_names: list[str] | None,
) -> list[str]:
    """Return a unique list of label_lower.

    Both app_labels and model_names are validated. Collects all errors
    and raises a single CommandError listing every unknown label/name
    so the operator can fix them all in one pass rather than one per
    re-run.
    """
    app_labels = list(app_labels or [])
    model_names = list(model_names or [])
    errors: list[str] = []

    for app_label in app_labels:
        try:
            django_apps.get_app_config(app_label)
        except LookupError:
            errors.append(f"unknown app_label `{app_label}`")

    for model_name in model_names:
        try:
            django_apps.get_model(model_name)
        except (LookupError, ValueError):
            errors.append(f"unknown model `{model_name}`")

    if errors:
        raise CommandError("Invalid --app / --model input: " + "; ".join(errors) + ".")

    for app_label in app_labels:
        app_config = django_apps.get_app_config(app_label)
        model_names.extend([cls._meta.label_lower for cls in app_config.get_models()])
    return list(set(model_names))


def get_site_ids_for_export(
    site_ids: list[int] | None,
    countries: list[str] | None,
) -> list[int]:
    """Return a list of site ids based on explicit `site_ids` or `countries`.

    `site_ids` and `countries` are mutually exclusive. The caller must
    pass exactly one (non-empty). An empty result from both inputs is
    treated as a programming error here; the management command is
    expected to reject "neither specified" before calling this function.
    """
    site_ids = list(site_ids or [])
    countries = list(countries or [])

    if countries and site_ids:
        raise CommandError("Invalid. Specify `site_ids` or `countries`, not both.")

    if site_ids:
        site_model_cls = django_apps.get_model("sites.site")
        validated: list[int] = []
        for site_id in site_ids:
            try:
                obj = site_model_cls.objects.get(id=int(site_id))
            except ObjectDoesNotExist as e:
                raise CommandError(f"Invalid site_id. Got `{site_id}`.") from e
            validated.append(obj.id)
        return validated

    resolved: list[int] = []
    for country in countries:
        resolved.extend(list(site_sites.get_by_country(country)))
    return resolved
