from edc_appointment.view_mixins import AppointmentViewMixin
from edc_metadata.view_mixins import MetaDataViewMixin
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from .subject_dashboard import ConsentViewMixin, ShowHideViewMixin
from .subject_identifier_view_mixin import SubjectIdentifierViewMixin


class SubjectDashboardViewMixin(
        ShowHideViewMixin, SubjectIdentifierViewMixin, ConsentViewMixin,
        VisitScheduleViewMixin, AppointmentViewMixin, MetaDataViewMixin):

    pass
