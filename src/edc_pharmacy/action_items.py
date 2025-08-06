from edc_action_item import Action, site_action_items
from edc_constants.constants import HIGH_PRIORITY

from .constants import PRESCRIPTION_ACTION


class PrescriptionAction(Action):
    name = PRESCRIPTION_ACTION
    display_name = "New prescription"
    reference_model = "edc_pharmacy.rx"
    priority = HIGH_PRIORITY
    show_on_dashboard = True
    show_link_to_changelist = True
    admin_site_name = "edc_pharmacy_admin"
    create_by_user = False
    singleton = True
    instructions = (
        "This prescription will cover the participant for the period on study. "
        "All refills are written against this prescription."
    )

    def reopen_action_item_on_change(self):
        return False


site_action_items.register(PrescriptionAction)
