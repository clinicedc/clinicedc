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
        return self.reference_model_cls.objects.get_requisition_for_visit(
            visit=self.visit,
            model=self.model,
            panel_name=self.target_panel)
