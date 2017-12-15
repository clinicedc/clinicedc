from ..action import Action
from ..action_items import ReminderAction
from ..site_action_items import site_action_items
from ..constants import HIGH_PRIORITY


class TestDoNothingPrnAction(Action):

    name = 'test-nothing-prn-action'
    display_name = 'Test Prn Action'


class TestPrnAction(Action):

    name = 'test-prn-action'
    display_name = 'Test Prn Action'
    next_actions = [ReminderAction]


class FormThreeAction(Action):
    name = 'submit-form-three'
    display_name = 'Submit Form Three'
    model = 'edc_action_item.formthree'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [ReminderAction]


class FormTwoAction(Action):
    name = 'submit-form-two'
    display_name = 'Submit Form Two'
    model = 'edc_action_item.formtwo'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    parent_model_fk_attr = 'form_one'
    next_actions = ['self']


class FormOneAction(Action):
    name = 'submit-form-one'
    display_name = 'Submit Form One'
    model = 'edc_action_item.formone'
    show_on_dashboard = True
    priority = HIGH_PRIORITY
    next_actions = [FormTwoAction, FormThreeAction]


class FormZeroAction(Action):
    name = 'submit-form-zero'
    display_name = 'Submit Form Zero'
    model = 'edc_action_item.formzero'
    show_on_dashboard = True
    priority = HIGH_PRIORITY


site_action_items.register(FormZeroAction)
site_action_items.register(FormOneAction)
site_action_items.register(FormTwoAction)
site_action_items.register(FormThreeAction)
site_action_items.register(TestDoNothingPrnAction)
site_action_items.register(TestPrnAction)
