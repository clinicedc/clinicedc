from django.apps import apps as django_apps
from edc_reference import get_reference_name, site_reference_configs
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import REQUISITION
from ..target_handler import TargetHandler
from .requisition_metadata_handler import RequisitionMetadataHandler


class TargetPanelNotScheduledForVisit(Exception):
    pass


class InvalidTargetPanel(Exception):
    pass


class RequisitionTargetHandler(TargetHandler):

    metadata_handler_cls = RequisitionMetadataHandler
    metadata_category = REQUISITION

    def __init__(self, target_panel=None, **kwargs):
        try:
            self.target_panel = target_panel.name
        except AttributeError:
            self.target_panel = target_panel
        super().__init__(**kwargs)

    @property
    def reference_model_cls(self):
        name = get_reference_name(self.model, self.target_panel)
        reference_model = site_reference_configs.get_reference_model(
            name=name)
        return django_apps.get_model(reference_model)

    @property
    def object(self):
        return self.reference_model_cls.objects.get_requisition_for_visit(
            visit=self.visit,
            name=get_reference_name(self.model, self.target_panel))

    @property
    def target_panels(self):
        """Returns a list of panels for this visit.
        """
        if self.visit.visit_code_sequence != 0:
            forms = (self.visit.visit.requisitions_unscheduled
                     + self.visit.visit.requisitions_prn)
        else:
            forms = self.visit.visit.requisitions + self.visit.visit.requisitions_prn
        return list(set([form.panel.name for form in forms]))

    def raise_on_not_scheduled_for_visit(self):
        """Raises an exception if target_panel is not scheduled
        for this visit or is invalid.
        """
        self.raise_on_invalid_panel()
        if self.target_panel not in self.target_panels:
            raise TargetPanelNotScheduledForVisit(
                f'Target panel {self.target_panel} is not scheduled '
                f'for visit \'{self.visit.visit_code}\'.')

    @property
    def schedule(self):
        """Returns a schedule instance from site_visit_schedule
        for this visit.
        """
        visit_schedule = site_visit_schedules.get_visit_schedule(
            self.visit.visit_schedule_name)
        return visit_schedule.schedules.get(self.visit.schedule_name)

    def raise_on_invalid_panel(self):
        """Raises an exception if target_panel is not found in any visit
        for this schedule.
        """
        panel_names = []
        for visit in self.schedule.visits.values():
            panel_names.extend([r.panel.name for r in visit.all_requisitions])
        if self.target_panel not in panel_names:
            raise InvalidTargetPanel(
                f'Invalid panel. {self.target_panel} is not a valid '
                f'panel for any visit in schedule {repr(self.schedule)}. ')

    @property
    def metadata_handler(self):
        return self.metadata_handler_cls(
            metadata_model=self.metadata_model,
            model=self.model,
            visit=self.visit,
            panel=self.target_panel)
