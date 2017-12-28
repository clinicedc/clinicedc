from edc_action_item.action import Action
from edc_action_item.constants import HIGH_PRIORITY
from edc_action_item.site_action_items import site_action_items

SUBJECT_LOCATOR_ACTION = 'submit-subject-locator'


class SubjectLocatorAction(Action):
    name = SUBJECT_LOCATOR_ACTION
    display_name = 'Submit Subject Locator'
    model = 'edc_locator.subjectlocator'
    show_link_to_changelist = True
    admin_site_name = 'edc_locator_admin'
    priority = HIGH_PRIORITY


site_action_items.register(SubjectLocatorAction)
