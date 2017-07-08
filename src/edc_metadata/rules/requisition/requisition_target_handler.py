from django.core.exceptions import ObjectDoesNotExist

from ..target_handler import TargetHandler


class RequisitionTargetHandler(TargetHandler):

    def __init__(self, target_panel=None, **kwargs):
        try:
            self.target_panel = target_panel.name
        except AttributeError:
            self.target_panel = target_panel
        super().__init__(**kwargs)

    @property
    def object(self):
        opts = {}
        if self.target_panel:
            opts = dict(panel_name=self.target_panel)
        try:
            return self.model.objects.get_for_visit(self.visit, **opts)
        except ObjectDoesNotExist:
            return None
