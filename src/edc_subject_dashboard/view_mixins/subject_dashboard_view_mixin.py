from edc_consent.view_mixins import ConsentViewMixin
from edc_locator.view_mixins import SubjectLocatorViewMixin

from edc_action_item.view_mixins import ActionItemViewMixin
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_metadata.view_mixins import MetaDataViewMixin
from edc_offstudy.view_mixins import SubjectOffstudyViewMixin
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from .show_hide_forms_view_mixin import ShowHideViewMixin
from .registered_subject_view_mixin import RegisteredSubjectViewMixin
from .subject_visit_view_mixin import SubjectVisitViewMixin
from ..model_wrappers import ActionItemModelWrapper


class SubjectDashboardViewMixin(
        MetaDataViewMixin,
        ConsentViewMixin,
        SubjectLocatorViewMixin,
        AppointmentViewMixin,
        ActionItemViewMixin,
        SubjectVisitViewMixin,
        VisitScheduleViewMixin,
        # SubjectOffstudyViewMixin,
        ShowHideViewMixin,
        RegisteredSubjectViewMixin):

    action_item_model_wrapper_cls = ActionItemModelWrapper
