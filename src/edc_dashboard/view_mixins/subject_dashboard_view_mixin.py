from .subject_dashboard import (
    MetaDataMixin, ConsentMixin, AppointmentMixin, VisitScheduleViewMixin,
    ShowHideViewMixin)
from .subject_identifier_view_mixin import SubjectIdentifierViewMixin


class SubjectDashboardViewMixin(
        ShowHideViewMixin, SubjectIdentifierViewMixin, ConsentMixin,
        VisitScheduleViewMixin, AppointmentMixin, MetaDataMixin):

    """Adds the show form attr from the URL."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_forms = None

    def get(self, request, *args, **kwargs):
        """Overidden to add show_forms to the view instance."""
        self.show_forms = kwargs.get('show_forms')
        return super().get(request, *args, **kwargs)
