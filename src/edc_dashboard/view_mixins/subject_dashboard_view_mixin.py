from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from .subject_dashboard import (
    MetaDataViewMixin, ConsentViewMixin, AppointmentViewMixin,
    ShowHideViewMixin)
from .subject_identifier_view_mixin import SubjectIdentifierViewMixin


class SubjectDashboardViewMixin(
        ShowHideViewMixin, SubjectIdentifierViewMixin, ConsentViewMixin,
        VisitScheduleViewMixin, AppointmentViewMixin, MetaDataViewMixin):

    pass
