from .action import Action
from .constants import MEDIUM_PRIORITY, HIGH_PRIORITY
from .site_action_items import site_action_items


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
