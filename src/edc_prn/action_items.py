from django.utils.safestring import mark_safe
from edc_action_item import ActionWithNotification
from edc_constants.constants import CLOSED, HIGH_PRIORITY, TBD, YES
from edc_offstudy.constants import END_OF_STUDY_ACTION

from .constants import (
    PROTOCOL_DEVIATION_VIOLATION_ACTION,
    UNBLINDING_REQUEST_ACTION,
    UNBLINDING_REVIEW_ACTION,
)


class ProtocolDeviationViolationAction(ActionWithNotification):

    reference_model = None  # "ambition_prn.protocoldeviationviolation"
    admin_site_name = None  # "ambition_prn_admin"

    name = PROTOCOL_DEVIATION_VIOLATION_ACTION
    display_name = "Submit Protocol Deviation/Violation Report"
    notification_display_name = "Protocol Deviation/Violation Report"
    parent_action_names = []
    show_link_to_changelist = True
    show_link_to_add = True
    priority = HIGH_PRIORITY

    def close_action_item_on_save(self):
        return self.reference_obj.report_status == CLOSED


class UnblindingRequestAction(ActionWithNotification):

    reference_model = None  # "inte_prn.unblindingrequest"
    admin_site_name = None  # "inte_prn_admin"

    name = UNBLINDING_REQUEST_ACTION
    display_name = "Unblinding request"
    notification_display_name = " Unblinding request"
    parent_action_names = []
    show_link_to_changelist = True
    show_link_to_add = True
    priority = HIGH_PRIORITY

    def get_next_actions(self):
        next_actions = []
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=UNBLINDING_REVIEW_ACTION,
            required=self.reference_obj.approved == TBD,
        )
        return next_actions


class UnblindingReviewAction(ActionWithNotification):

    reference_model = None  # "inte_prn.unblindingreview"
    admin_site_name = None  # "inte_prn_admin"

    name = UNBLINDING_REVIEW_ACTION
    display_name = "Unblinding review pending"
    notification_display_name = " Unblinding review needed"
    parent_action_names = [UNBLINDING_REQUEST_ACTION]
    show_link_to_changelist = True
    priority = HIGH_PRIORITY
    color_style = "info"
    create_by_user = False
    instructions = mark_safe(
        "This report is to be completed by the UNBLINDING REVIEWERS only."
    )

    def get_next_actions(self):
        next_actions = []
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=END_OF_STUDY_ACTION,
            required=self.reference_obj.approved == YES,
        )
        return next_actions
