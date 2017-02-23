from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from edc_base.utils import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin

from ...forms import PackAliquotsForm
from ...models import Destination, Manifest


class PackView(EdcBaseViewMixin, AppConfigViewMixin, FormView):

    template_name = 'edc_lab/home.html'
    navbar_name = 'specimens'
    form_class = PackAliquotsForm

    @property
    def app_config(self):
        return django_apps.get_app_config('edc_lab')

    @property
    def aliquot_model(self):
        return django_apps.get_model(*self.app_config.aliquot_model.split('.'))

    def get_success_url(self):
        return reverse(self.app_config.aliquot_listboard_url_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        valid = {}
        invalid = []
        aliquot_identifiers = form.data.get('aliquot_identifiers')
        aliquot_identifiers = aliquot_identifiers.split('\n')
        aliquot_identifiers = [x.strip() for x in aliquot_identifiers]
        aliquot_identifiers = list(set(aliquot_identifiers))
        for aliquot_identifier in aliquot_identifiers:
            try:
                obj = self.aliquot_model.objects.get(
                    aliquot_identifier=aliquot_identifier,
                    packed=False)
            except self.aliquot_model.DoesNotExist:
                invalid.append(aliquot_identifier)
            else:
                valid.update({aliquot_identifier: obj})
        self.pack_aliquots(
            aliquots=valid,
            destination=form.data.get('destination'),
            manifest_identifier=form.data.get('manifest'))
        self.add_pending_results(aliquots=valid)
        return super().form_valid(form)

    def pack_aliquots(self, aliquots=None, destination=None, manifest_identifier=None):
        if manifest_identifier:
            manifest = Manifest.objects.get(
                manifest_identifier=manifest_identifier)
        else:
            destination = Destination.objects.get(name=destination)
            manifest = Manifest.objects.create(
                destination=destination,
                user_created=self.request.user.username)
        self.aliquot_model.objects.filter(
            aliquot_identifier__in=list(aliquots.keys()),
            packed=False).update(
                packed=True,
                packed_datetime=get_utcnow(),
                manifest=manifest,
                user_modified=self.request.user.username)

    def add_pending_results(self, aliquots=None):
        pass
