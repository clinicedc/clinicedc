from edc_visit_schedule import site_visit_schedules
from edc_visit_schedule.models import SubjectScheduleHistory


class VisitScheduleActionMixin:

    """A mixin for the Action class to add properties and
    methods related to the visit schedule from
    edc_visit_schedule.
    """

    def __init__(self, reference_obj=None, subject_identifier=None, **kwargs):
        super().__init__(
            reference_obj=reference_obj, subject_identifier=subject_identifier, **kwargs
        )
        self.offschedule_model = None
        if reference_obj and subject_identifier:
            for onschedule_model_obj in SubjectScheduleHistory.objects.onschedules(
                subject_identifier=subject_identifier,
                report_datetime=reference_obj.report_datetime,
            ):
                _, schedule = site_visit_schedules.get_by_onschedule_model(
                    onschedule_model=onschedule_model_obj._meta.label_lower
                )
                self.offschedule_model = schedule.offschedule_model
