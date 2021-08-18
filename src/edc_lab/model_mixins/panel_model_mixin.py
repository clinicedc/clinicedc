from django.db import models
from django.db.models.deletion import PROTECT

from ..site_labs import site_labs


class PanelModelError(Exception):
    pass


class LabProfileError(Exception):
    pass


class NothingPanel:
    verbose_name = None


class PanelModelMixin(models.Model):

    panel = models.ForeignKey("edc_lab.Panel", on_delete=PROTECT, null=True)

    @property
    def panel_object(self):
        """Returns a `panel` or `panel group` object"""
        try:
            panel_name = self.panel.name
        except AttributeError:
            panel_object = NothingPanel()
        else:
            try:
                panel_object = self.lab_profile_object.panels[panel_name]
            except KeyError as e:
                raise PanelModelError(
                    "Undefined `panel` name or `panel group` name. "
                    f"Got {panel_name}. See LabProfile and model Panel. Got {e}"
                )
        return panel_object

    @property
    def lab_profile_object(self):
        lab_profile_object = site_labs.get(self.panel.lab_profile_name)
        if not lab_profile_object:
            raise LabProfileError(
                f"Undefined lab profile name detected from panel {self.panel}. "
                f"Expected one of {site_labs.lab_profiles}. "
                f"Got '{self.panel.lab_profile_name}'. "
                "See stored values in panel model."
            )
        return lab_profile_object

    class Meta:
        abstract = True
