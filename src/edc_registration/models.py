from edc_base.model_mixins import BaseUuidModel
from edc_base.sites.managers import CurrentSiteManager
from edc_base.sites.site_model_mixin import SiteModelMixin

from .managers import RegisteredSubjectManager
from .model_mixins import RegisteredSubjectModelMixin


class RegisteredSubject(RegisteredSubjectModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = RegisteredSubjectManager()

    def natural_key(self):
        return super().natural_key()
    natural_key.dependencies = ['sites.Site']

    class Meta:
        app_label = 'edc_registration'
