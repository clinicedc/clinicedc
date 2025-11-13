from __future__ import annotations

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
from edc_dashboard.view_mixins import EdcViewMixin

from ..constants import CSV
from ..exportable_models_for_user import ExportableModelsForUser
from ..files_emailer import FilesEmailerError
from ..model_options import ModelOptions
from ..models_to_file import ModelsToFile, ModelsToFileNothingExportedError
from ..utils import email_files_to_user, update_data_request_history

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class ExportModelsViewError(Exception):
    pass


class ExportSelectedModelsView(EdcViewMixin, TemplateView):
    post_action_url = "edc_export:export_models_url"
    template_name = "edc_export/export_models.html"

    def get_context_data(self, **kwargs) -> dict:
        if self.request.session.get("selected_models"):
            kwargs.update(
                selected_models=[
                    ModelOptions(**dct) for dct in self.request.session["selected_models"]
                ]
            )
        return super().get_context_data(**kwargs)

    def post(self, request: WSGIRequest, *args, **kwargs) -> HttpResponseRedirect:  # noqa: ARG002
        if not self.check_user(request):
            pass
        elif not request.user.email:
            user_url = reverse("admin:auth_user_change", args=(request.user.id,))
            messages.error(
                request,
                format_html(
                    "Your account does not include an email address. "
                    'Please update your <a href="{user_url}">user account</a> '
                    "and try again.",
                    user_url=mark_safe(user_url),  # nosec B308 B703
                ),
            )
        else:
            selected_models = self.check_export_permissions(
                self.get_selected_models_from_session(request)
                or self.get_selected_models_from_post(request)
            )
            selected_models = [x.label_lower for x in selected_models]
            if not selected_models:
                messages.warning(
                    request,
                    "Nothing to do. Select one or more models and try again.",
                )
            else:
                try:
                    models_to_file = ModelsToFile(
                        models=selected_models,
                        user=request.user,
                        archive_to_single_file=True,
                        export_format=CSV,
                    )
                except ModelsToFileNothingExportedError as e:
                    messages.warning(request, f"Nothing to do. {e}.")
                else:
                    if settings.DEBUG:
                        messages.success(
                            request,
                            (
                                "Your data request has been saved to "
                                f"{models_to_file.archive_filename}. settings.DEBUG=True."
                            ),
                        )
                        update_data_request_history(request, models_to_file)
                    else:
                        try:
                            email_files_to_user(request, models_to_file)
                        except FilesEmailerError as e:
                            messages.error(
                                request, f"Failed to send the data you requested. Got '{e}'"
                            )
                        update_data_request_history(request, models_to_file)

        url = reverse(self.post_action_url, kwargs=self.kwargs)
        return HttpResponseRedirect(url)

    @staticmethod
    def check_export_permissions(selected_models) -> list[ModelOptions]:
        return selected_models

    @staticmethod
    def get_selected_models_from_post(request: WSGIRequest) -> list[ModelOptions]:
        """Returns a list of selected models from the POST
        as ModelOptions.
        """
        exportables = ExportableModelsForUser(request=request, user=request.user)
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
