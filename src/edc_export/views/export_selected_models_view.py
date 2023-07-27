from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from edc_dashboard.utils import get_bootstrap_version
from edc_dashboard.view_mixins import EdcViewMixin

from ..archive_exporter import (
    ArchiveExporter,
    ArchiveExporterEmailError,
    ArchiveExporterNothingExported,
)
from ..exportables import Exportables
from ..files_emailer import FilesEmailerError
from ..model_options import ModelOptions
from ..models import DataRequest, DataRequestHistory

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class NothingToExport(Exception):
    pass


class ExportModelsViewError(Exception):
    pass


class ExportSelectedModelsView(EdcViewMixin, TemplateView):
    post_action_url = "edc_export:export_models_url"
    template_name = f"edc_export/bootstrap{get_bootstrap_version()}/export_models.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        if self.request.session.get("selected_models"):
            context.update(
                selected_models=[
                    ModelOptions(**dct) for dct in self.request.session["selected_models"]
                ]
            )
        return context

    def post(self, request: WSGIRequest, *args, **kwargs) -> HttpResponseRedirect:
        if not self.check_user(request):
            pass
        elif not request.user.email:
            user_url = reverse("admin:auth_user_change", args=(request.user.id,))
            messages.error(
                request,
                format_html(
                    "Your account does not include an email address. "
                    'Please update your <a href="{}">user account</a> '
                    "and try again.",
                    mark_safe(user_url),  # nosec B308 B703
                ),
            )
        else:
            try:
                self.export_models(request=request, email_to_user=True)
            except NothingToExport:
                messages.warning(
                    request,
                    "Nothing to do. Select one or more models and try again.",
                )
            except FilesEmailerError as e:
                messages.error(request, f"Failed to send the data you requested. Got '{e}'")
        url = reverse(self.post_action_url, kwargs=self.kwargs)
        return HttpResponseRedirect(url)

    @staticmethod
    def check_export_permissions(selected_models) -> list[ModelOptions]:
        return selected_models

    def export_models(self, request: WSGIRequest = None, email_to_user=None):
        selected_models = self.check_export_permissions(
            self.get_selected_models_from_session(request)
            or self.get_selected_models_from_post(request)
        )
        selected_models = [x.label_lower for x in selected_models]
        email_to_user = False if settings.DEBUG else email_to_user
        archive = True if settings.DEBUG else False
        try:
            exporter = ArchiveExporter(
                models=selected_models,
                user=request.user,
                email_to_user=email_to_user,
                archive=archive,
            )
        except (ArchiveExporterEmailError, ConnectionRefusedError) as e:
            messages.error(request, f"Failed to send files by email. Got '{e}'")
        except ArchiveExporterNothingExported:
            messages.info(request, "Nothing to export.")
        else:
            if email_to_user:
                msg = (
                    f"Your data request has been sent to {request.user.email}. "
                    "Please check your email."
                )
            else:
                msg = f"Your data request has been saved to {exporter.archive_filename}. "

            messages.success(request, msg)
            summary = [str(x) for x in exporter.exported]
            summary.sort()
            data_request = DataRequest.objects.create(
                name=f'Data request {datetime.now().strftime("%Y%m%d%H%M")}',
                models="\n".join(selected_models),
                user_created=request.user.username,
                site=request.site,
            )
            DataRequestHistory.objects.create(
                data_request=data_request,
                exported_datetime=exporter.exported_datetime,
                summary="\n".join(summary),
                user_created=request.user.username,
                user_modified=request.user.username,
                archive_filename=exporter.archive_filename,
                emailed_to=exporter.emailed_to,
                emailed_datetime=exporter.emailed_datetime,
                site=request.site,
            )

    @staticmethod
    def get_selected_models_from_post(request: WSGIRequest) -> list[ModelOptions]:
        """Returns a list of selected models from the POST
        as ModelOptions.
        """
        exportables = Exportables(request=request, user=request.user)
        selected_models = []
        for exportable in exportables:
            selected_models.extend(request.POST.getlist(f"chk_{exportable}_models") or [])
            selected_models.extend(
                request.POST.getlist(f"chk_{exportable}_historical_models") or []
            )
            selected_models.extend(request.POST.getlist(f"chk_{exportable}_list_models") or [])
            selected_models.extend(request.POST.getlist(f"chk_{exportable}_inlines") or [])
        if selected_models:
            selected_models = [ModelOptions(model=m) for m in selected_models if m]
        return selected_models

    @staticmethod
    def get_selected_models_from_session(request: WSGIRequest) -> list[ModelOptions]:
        """Returns a list of selected models from the session object
        as ModelOptions.
        """
        try:
            selected_models = request.session.pop("selected_models")
        except KeyError:
            selected_models = []
        else:
            selected_models = [ModelOptions(**dct) for dct in selected_models]
        return selected_models

    def check_user(self, request) -> bool:
        try:
            valid_user = User.objects.filter(username=self.request.user).exists()
        except ObjectDoesNotExist:
            messages.error(request, "Invalid user.")
            valid_user = False
        return valid_user
