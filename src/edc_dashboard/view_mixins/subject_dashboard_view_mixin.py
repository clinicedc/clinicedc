from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from .subject_dashboard import (
    MetaDataViewMixin, ConsentViewMixin, AppointmentViewMixin,
    ShowHideViewMixin)
from .subject_identifier_view_mixin import SubjectIdentifierViewMixin


class SubjectDashboardViewMixin(
        ShowHideViewMixin, SubjectIdentifierViewMixin, ConsentViewMixin,
        VisitScheduleViewMixin, AppointmentViewMixin, MetaDataViewMixin):

    """Adds the show form attr from the URL.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_forms = None

    def get(self, request, *args, **kwargs):
        """Overidden to add show_forms to the view instance."""
        self.show_forms = kwargs.get('show_forms')
        return super().get(request, *args, **kwargs)
