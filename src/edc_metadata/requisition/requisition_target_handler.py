from ..target_handler import TargetHandler
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class TargetPanelNotScheduledForVisit(Exception):
    pass


class InvalidTargetPanel(Exception):
    pass


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

    def raise_on_not_scheduled_for_visit(self):
        """Raises an exception if target_panel is not scheduled
        for this visit.

        Overridden.
        """

        self.raise_on_invalid_panel()

        requisitions = self.schedule.visits.get(
            self.visit.visit_code).requisitions
        if self.target_panel not in [r.panel.name for r in requisitions]:
            raise TargetPanelNotScheduledForVisit(
                f'Target panel {self.target_panel} is not scheduled '
                f'for visit \'{self.visit.visit_code}\'.')

    @property
    def schedule(self):
        """Returns a schedule instance from site_visit_schedule
        for this visit.
        """
        return site_visit_schedules.get_schedule(
            visit_schedule_name=self.visit.visit_schedule_name,
            schedule_name=self.visit.schedule_name)

    def raise_on_invalid_panel(self):
        """Raises an exception if target_panel is invalid.
        """
        panel_names = []
        for visit in self.schedule.visits.values():
            panel_names.extend([r.panel.name for r in visit.requisitions])
        if self.target_panel not in panel_names:
            raise InvalidTargetPanel(
                f'{self.target_panel} is not a valid panel name.')
