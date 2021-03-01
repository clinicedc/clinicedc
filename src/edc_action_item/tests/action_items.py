from edc_constants.constants import HIGH_PRIORITY, NO

from ..action import Action
from ..action_with_notification import ActionWithNotification
from ..site_action_items import site_action_items


class FormZeroAction(ActionWithNotification):
    name = "submit-form-zero"
    display_name = "Submit Form Zero"
    reference_model = "edc_action_item.formzero"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    parent_action_names = ["submit-form-three"]

    notification_display_name = "a form zero event has occured"
    notification_fields = ["f1"]
    notification_email_to = ["someone@example.com"]


class TestDoNothingPrnAction(Action):

    name = "test-nothing-prn-action"
    display_name = "Test Nothing Prn Action"
    parent_action_names = None


class TestPrnAction(Action):

    name = "test-prn-action"
    display_name = "Test Prn Action"
    next_actions = [FormZeroAction.name]
    parent_action_names = None


class FormThreeAction(Action):
    name = "submit-form-three"
    display_name = "Submit Form Three"
    reference_model = "edc_action_item.formthree"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [FormZeroAction.name]
    parent_action_names = ["submit-form-one"]


class FormTwoAction(Action):
    name = "submit-form-two"
    display_name = "Submit Form Two"
    reference_model = "edc_action_item.formtwo"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    related_reference_model = "edc_action_item.formone"
    related_reference_fk_attr = "form_one"
    next_actions = ["self"]
    parent_action_names = ["submit-form-two", "submit-form-one"]


class FormOneAction(Action):
    name = "submit-form-one"
    display_name = "Submit Form One"
    reference_model = "edc_action_item.formone"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [FormTwoAction.name, FormThreeAction.name]
    parent_action_names = ["submit-form-three", "submit-form-four"]


class FormFourAction(Action):
    name = "submit-form-four"
    display_name = "Submit Form Four"
    reference_model = "edc_action_item.formfour"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    parent_action_names = ["submit-form-one"]

    def get_next_actions(self):
        next_actions = []
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=FormOneAction.name,
            required=self.reference_obj.happy == NO,
        )
        return next_actions


class FollowupAction(Action):
    name = "submit-followup"
    display_name = "Submit Followup"
    reference_model = "edc_action_item.followup"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = ["self"]
    related_reference_fk_attr = "initial"
    related_reference_model = "edc_action_item.initial"
    parent_action_names = ["submit-followup", "submit-initial"]


class CrfTwoAction(Action):
    name = "submit-crf-two"
    display_name = "Submit Crf Two"
    reference_model = "edc_action_item.crftwo"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = ["self"]
    parent_action_names = ["submit-crf-two", "submit-crf-one"]


class CrfOneAction(Action):
    name = "submit-crf-one"
    display_name = "Submit Crf One"
    reference_model = "edc_action_item.crfone"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [CrfTwoAction.name]


class InitialAction(Action):
    name = "submit-initial"
    display_name = "Submit Initial"
    reference_model = "edc_action_item.initial"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [FollowupAction.name]


class SingletonAction(Action):
    name = "singleton"
    display_name = "Singleton"
    reference_model = "edc_action_item.formzero"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    singleton = True


class CrfLongitudinalTwoAction(Action):
    name = "submit-crf-longitudinal-two"
    display_name = "Submit Crf Two"
    reference_model = "edc_action_item.crflongitudinaltwo"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = None
    parent_action_names = ["submit-crf-longitudinal-one"]


class CrfLongitudinalOneAction(Action):
    name = "submit-crf-longitudinal-one"
    display_name = "Submit Crf One"
    reference_model = "edc_action_item.crflongitudinalone"
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [CrfLongitudinalTwoAction.name]


def register_actions():
    site_action_items.registry = {}
    site_action_items.register(FormZeroAction)
    site_action_items.register(FormOneAction)
    site_action_items.register(FormTwoAction)
    site_action_items.register(FormThreeAction)
    site_action_items.register(FormFourAction)
    site_action_items.register(InitialAction)
    site_action_items.register(FollowupAction)
    site_action_items.register(TestDoNothingPrnAction)
    site_action_items.register(TestPrnAction)
    site_action_items.register(SingletonAction)
    site_action_items.register(CrfOneAction)
    site_action_items.register(CrfTwoAction)
    site_action_items.register(CrfLongitudinalOneAction)
    site_action_items.register(CrfLongitudinalTwoAction)
