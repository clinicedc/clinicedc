from django.conf import settings
from django.template.loader import render_to_string
from edc_action_item import Action, site_action_items
from edc_constants.constants import (
    CLOSED,
    RESOLVED,
    FEEDBACK,
    HIGH_PRIORITY,
    MEDIUM_PRIORITY,
    NORMAL,
)
from edc_utils.date import get_utcnow

from .constants import CLOSED_WITH_ACTION


DATA_QUERY_ACTION = "data_query_action"
SHOW_ON_DASHBOARD = getattr(settings, "DATA_MANAGER_SHOW_ON_DASHBOARD", True)


class DataQueryAction(Action):
    name = DATA_QUERY_ACTION
    display_name = "Data query"
    reference_model = "edc_data_manager.dataquery"
    priority = MEDIUM_PRIORITY
    create_by_user = True
    show_link_to_changelist = True
    show_on_dashboard = SHOW_ON_DASHBOARD
    admin_site_name = "edc_data_manager_admin"
    instructions = "Review and respond to the query"
    delete_with_reference_object = True

    def reopen_action_item_on_change(self):
        return not self.close_action_item_on_save()

    def close_action_item_on_save(self):
        if self.reference_obj and self.reference_obj.status in [
            CLOSED,
            CLOSED_WITH_ACTION,
        ]:
            return True
        return False

    def get_priority(self):
        return self.query_priority or self.priority

    def get_popover_title(self):
        return self.get_category()

    @property
    def site_response_status(self):
        try:
            site_response_status = self.reference_obj.site_response_status
        except AttributeError:
            site_response_status = None
        return site_response_status

    @property
    def query_priority(self):
        try:
            query_priority = self.reference_obj.query_priority
        except AttributeError:
            query_priority = None
        return query_priority

    def get_color_style(self):
        color_style = "warning"
        if self.site_response_status in [FEEDBACK, RESOLVED]:
            color_style = "info"
        return color_style

    def get_category(self):
        return (
            "DM Query"
            if self.site_response_status in [FEEDBACK, RESOLVED]
            else "Site Query"
        )

    def get_status(self):
        if self.reference_obj:
            return self.reference_obj.get_site_response_status_display()
        return "New"

    def get_display_name(self):
        template_name = (
            f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/"
            f"action_item_display_name.html"
        )
        title = getattr(self.reference_obj, "title", "")
        visit_schedule = getattr(self.reference_obj, "visit_schedule", "")
        modified = getattr(self.reference_obj, "modified", None)
        auto = "auto" if getattr(self.reference_obj, "rule_generated", False) else ""
        try:
            query_priority = self.reference_obj.get_query_priority_display()
        except AttributeError:
            query_priority = NORMAL
        context = dict(
            HIGH_PRIORITY=HIGH_PRIORITY,
            auto=auto,
            category=self.get_category(),
            modified=modified,
            object=self.reference_obj,
            query_priority=query_priority,
            title=title,
            utcnow=get_utcnow(),
            visit_schedule=visit_schedule,
        )
        form_and_numbers_to_string = getattr(
            self.reference_obj, "form_and_numbers_to_string", None
        )
        if form_and_numbers_to_string:
            context.update(form_and_numbers=form_and_numbers_to_string())
        return render_to_string(template_name, context=context)


site_action_items.register(DataQueryAction)
