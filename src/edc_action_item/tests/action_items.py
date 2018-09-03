from ..action import Action
from ..site_action_items import site_action_items
from ..constants import HIGH_PRIORITY


class FormZeroAction(Action):
    name = 'submit-form-zero'
    display_name = 'Submit Form Zero'
    reference_model = 'edc_action_item.formzero'
    show_on_dashboard = True
    priority = HIGH_PRIORITY


class TestDoNothingPrnAction(Action):

    name = 'test-nothing-prn-action'
    display_name = 'Test Prn Action'


class TestPrnAction(Action):

    name = 'test-prn-action'
    display_name = 'Test Prn Action'
    next_actions = [FormZeroAction]


class FormThreeAction(Action):
    name = 'submit-form-three'
    display_name = 'Submit Form Three'
    reference_model = 'edc_action_item.formthree'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [FormZeroAction]


class FormTwoAction(Action):
    name = 'submit-form-two'
    display_name = 'Submit Form Two'
    reference_model = 'edc_action_item.formtwo'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    related_reference_model = 'edc_action_item.formone'
    related_reference_fk_attr = 'form_one'
    next_actions = ['self']


class FormOneAction(Action):
    name = 'submit-form-one'
    display_name = 'Submit Form One'
    reference_model = 'edc_action_item.formone'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [FormTwoAction, FormThreeAction]


class FollowupAction(Action):
    name = 'submit-followup'
    display_name = 'Submit Followup'
    reference_model = 'edc_action_item.followup'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = ['self']
    related_reference_fk_attr = 'initial'
    related_reference_model = 'edc_action_item.initial'


class CrfTwoAction(Action):
    name = 'submit-crf-two'
    display_name = 'Submit Crf Two'
    reference_model = 'edc_action_item.crftwo'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = ['self']


class CrfOneAction(Action):
    name = 'submit-crf-one'
    display_name = 'Submit Crf One'
    reference_model = 'edc_action_item.crfone'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [CrfTwoAction]


class InitialAction(Action):
    name = 'submit-initial'
    display_name = 'Submit Initial'
    reference_model = 'edc_action_item.initial'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [FollowupAction]


class SingletonAction(Action):
    name = 'singleton'
    display_name = 'Singleton'
    reference_model = 'edc_action_item.formzero'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    singleton = True


def register_actions():
    site_action_items.registry = {}
    site_action_items.register(FormZeroAction)
    site_action_items.register(FormOneAction)
    site_action_items.register(FormTwoAction)
    site_action_items.register(FormThreeAction)
    site_action_items.register(InitialAction)
    site_action_items.register(FollowupAction)
    site_action_items.register(TestDoNothingPrnAction)
    site_action_items.register(TestPrnAction)
    site_action_items.register(SingletonAction)
    site_action_items.register(CrfOneAction)
    site_action_items.register(CrfTwoAction)


register_actions()
