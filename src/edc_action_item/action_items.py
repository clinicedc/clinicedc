from .action import Action
from .constants import MEDIUM_PRIORITY, HIGH_PRIORITY
from django.conf import settings
from edc_action_item.site_action_items import site_action_items


class ReminderAction(Action):
    name = 'reminder'
    display_name = 'Reminder'
    show_on_dashboard = True
    priority = MEDIUM_PRIORITY


class UrgentReminderAction(Action):
    name = 'urgent-reminder'
    display_name = 'Urgent Reminder'
    show_on_dashboard = True
    priority = HIGH_PRIORITY


site_action_items.register(ReminderAction)
site_action_items.register(UrgentReminderAction)

if settings.APP_NAME == 'edc_action_item':

    class FormThreeAction(Action):
        name = 'submit-form-three'
        display_name = 'Submit Form Three'
        model = 'edc_action_item.formthree'
        show_on_dashboard = True
        priority = HIGH_PRIORITY
        create_actions = [ReminderAction]
        next_actions = []

    class FormTwoAction(Action):
        name = 'submit-form-two'
        display_name = 'Submit Form Two'
        model = 'edc_action_item.formtwo'
        show_on_dashboard = True
        priority = HIGH_PRIORITY
        parent_model_fk_attr = 'form_one'
        create_actions = []
        next_actions = ['self']

    class FormOneAction(Action):
        name = 'submit-form-one'
        display_name = 'Submit Form One'
        model = 'edc_action_item.formone'
        show_on_dashboard = True
        priority = HIGH_PRIORITY
        create_actions = []
        next_actions = [FormTwoAction, FormThreeAction]

    site_action_items.register(FormOneAction)
    site_action_items.register(FormTwoAction)
    site_action_items.register(FormThreeAction)
