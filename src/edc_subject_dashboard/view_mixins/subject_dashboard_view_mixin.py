from edc_appointment.view_mixins import AppointmentViewMixin
from edc_metadata.view_mixins import MetaDataViewMixin
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from .consent_view_mixin import ConsentViewMixin
from .show_hide_forms_view_mixin import ShowHideViewMixin
from .subject_identifier_view_mixin import SubjectIdentifierViewMixin
from .subject_locator_view_mixin import SubjectLocatorViewMixin
from .subject_visit_view_mixin import SubjectVisitViewMixin


class SubjectDashboardViewMixin(
        MetaDataViewMixin,
        ConsentViewMixin,
        SubjectLocatorViewMixin,
        SubjectVisitViewMixin,
        AppointmentViewMixin,
        VisitScheduleViewMixin,
        ShowHideViewMixin,
        SubjectIdentifierViewMixin):

    pass
