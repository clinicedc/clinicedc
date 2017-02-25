from django.db import models

from ..site_labs import site_labs
from ..exceptions import PanelError


class PanelModelMixin(models.Model):

    panel_name = models.CharField(
        max_length=25)

    @property
    def panel_object(self):
        try:
            panel_object = site_labs.get(
                self._meta.label_lower).panels[self.panel_name]
        except KeyError as e:
            raise PanelError(
                'Undefined panel name. Got {}. See AppConfig. Got {}'.format(
                    self.panel_name, str(e)))
        return panel_object

    class Meta:
        abstract = True
