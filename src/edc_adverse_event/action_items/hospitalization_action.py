from clinicedc_constants import HIGH_PRIORITY

from edc_action_item.action_with_notification import ActionWithNotification

from ..constants import HOSPITALIZATION_ACTION


class HospitalizationAction(ActionWithNotification):
    reference_model: str = None  # e.g. "intecomm_prn.hospitalization"
    admin_site_name: str = None  # e.g. "intecomm_prn_admin"

    name = HOSPITALIZATION_ACTION
    display_name = "Submit Hospitalization Report"
    notification_display_name = "Hospitalization"
    parent_action_names = ()
    show_link_to_changelist = True
    show_link_to_add = True
    priority = HIGH_PRIORITY
