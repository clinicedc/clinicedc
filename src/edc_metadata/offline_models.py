from django.apps import apps as django_apps

from edc_base.model_mixins import ListModelMixin
from django_collect_offline.site_offline_models import site_offline_models
from django_collect_offline.offline_model import OfflineModel

offline_models = []
app_config = django_apps.get_app_config('edc_metadata')
for model in app_config.get_models():
    if not issubclass(model, ListModelMixin):
        offline_models.append(model._meta.label_lower)

site_offline_models.register(offline_models, OfflineModel)
