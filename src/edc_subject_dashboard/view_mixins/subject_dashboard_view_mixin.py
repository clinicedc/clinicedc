from edc_action_item.view_mixins import ActionItemViewMixin
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_consent.view_mixins import ConsentViewMixin
from edc_locator.view_mixins import SubjectLocatorViewMixin
from edc_metadata.view_mixins import MetaDataViewMixin
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from .registered_subject_view_mixin import RegisteredSubjectViewMixin
from .subject_visit_view_mixin import SubjectVisitViewMixin


class SubjectDashboardViewMixin(
        MetaDataViewMixin,
        ConsentViewMixin,
        SubjectLocatorViewMixin,
        AppointmentViewMixin,
        ActionItemViewMixin,
        SubjectVisitViewMixin,
        VisitScheduleViewMixin,
        RegisteredSubjectViewMixin):

    pass
