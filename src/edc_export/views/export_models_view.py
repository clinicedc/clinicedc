from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin

from ..archive_exporter import ArchiveExporter, ArchiveExporterNothingExported
from ..archive_exporter import ArchiveExporterEmailError
from ..exportables import Exportables
from ..files_emailer import FilesEmailerError
from ..model_options import ModelOptions
from ..models import DataRequest, DataRequestHistory


class NothingToExport(Exception):
    pass


class ExportModelsViewError(Exception):
    pass


class ExportModelsView(EdcBaseViewMixin, TemplateView):

    post_action_url = 'edc_export:home_url'
    template_name = f'edc_export/bootstrap{settings.EDC_BOOTSTRAP}/home.html'

    def __init__(self, *args, **kwargs):
        self._selected_models_from_post = None
        self._selected_models_from_session = None
        self._selected_models = None
        self._user = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.session.get('selected_models'):
            context.update(
                selected_models=[
                    ModelOptions(**dct) for dct in self.request.session[
                        'selected_models']])
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.email:
            user_url = reverse(
                'admin:auth_user_change', args=(request.user.id, ))
            messages.error(
                request,
                mark_safe(
                    f'Your account does not include an email address. '
                    f'Please update your <a href="{user_url}">user account</a> '
                    f'and try again.'))
        else:
            try:
                self.export_models(request=request, email_to_user=True)
            except NothingToExport as e:
                selected_models = self.get_selected_models_from_post()
                if selected_models:
                    self.request.session['selected_models'] = selected_models
                else:
                    messages.warning(
                        request, f'Nothing to do. Select one or more models and try again.')
            except FilesEmailerError as e:
                messages.error(
                    request, f'Failed to send the data you requested. Got {e}')
        url = reverse(self.post_action_url, kwargs=self.kwargs)
        return HttpResponseRedirect(url)

    def check_export_permissions(self, selected_models):
        return selected_models

    def export_models(self, request=None, email_to_user=None):
        selected_models = self.check_export_permissions(
            self.get_selected_models_from_session())
        selected_models = [x.label_lower for x in selected_models]
        try:
            exporter = ArchiveExporter(
                models=selected_models,
                add_columns_for=['subject_visit_id', 'requisition_id'],
                user=self.user,
                request=request,
                email_to_user=email_to_user,
                archive=False)
        except ArchiveExporterEmailError as e:
            messages.error(
                self.request, f'Failed to send files by email. Got \'{e}\'')
        except ArchiveExporterNothingExported as e:
            messages.info(self.request, f'Nothing to export.')
        else:
            messages.success(
                request, (f'Your data request has been sent to {self.user.email}. '
                          f'Please check your email.'))
            summary = [str(x) for x in exporter.exported]
            summary.sort()
            data_request = DataRequest.objects.create(
                name=f'Data request {datetime.now().strftime("%Y%m%d%H%M")}',
                models='\n'.join(selected_models),
                user_created=self.user)
            DataRequestHistory.objects.create(
                data_request=data_request,
                exported_datetime=exporter.exported_datetime,
                summary='\n'.join(summary),
                user_created=self.user.username,
                user_modified=self.user.username,
                archive_filename=exporter.archive_filename,
                emailed_to=exporter.emailed_to,
                emailed_datetime=exporter.emailed_datetime)

    @property
    def allowed_selected_models(self):
        """Returns a list of selected models as ModelOptions.
        """
        if self._selected_models:
            selected_models = self.get_selected_models_from_session()
            self._selected_models = self.check_export_permissions(
                selected_models)
        return self._selected_models or []

    def get_selected_models_from_post(self):
        """Returns a list of selected models from the POST
        as ModelOptions.
        """
        exportables = Exportables(request=self.request, user=self.user)
        selected_models = []
        for app_config in exportables:
            selected_models.extend(self.request.POST.getlist(
                f'chk_{app_config.name}_models') or [])
            selected_models.extend(self.request.POST.getlist(
                f'chk_{app_config.name}_historicals') or [])
            selected_models.extend(self.request.POST.getlist(
                f'chk_{app_config.name}_lists') or [])
        return [ModelOptions(model=m).__dict__ for m in selected_models if m]

    def get_selected_models_from_session(self):
        """Returns a list of selected models from the seesion object
        as ModelOptions.
        """
        try:
            selected_models = self.request.session.pop('selected_models')
        except KeyError:
            raise NothingToExport('KeyError')
        else:
            if not selected_models:
                raise NothingToExport('Nothing to export')
        return [ModelOptions(**dct) for dct in selected_models]

    @property
    def user(self):
        if not self._user:
            self._user = User.objects.get(username=self.request.user)
        return self._user
