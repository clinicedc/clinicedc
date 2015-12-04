from edc_base.model.models import BaseUuidModel
from edc_locator.models import LocatorMixin


class Locator(LocatorMixin, BaseUuidModel):

    class Meta:
        app_label = 'example'
