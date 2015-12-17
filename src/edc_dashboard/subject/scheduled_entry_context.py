from edc.entry_meta_data.models import ScheduledEntryMetaData

from .base_scheduled_entry_context import BaseScheduledEntryContext


class ScheduledEntryContext(BaseScheduledEntryContext):

    """A Class used by the dashboard when rendering the
    list of scheduled entries to display under "Scheduled Forms"."""

    meta_data_model = ScheduledEntryMetaData

    def contribute_to_context(self, context):
        context.update({'entry': self.meta_data_instance.entry,
                        'entry_order': self.meta_data_instance.entry.entry_order,
                        'group_title': self.meta_data_instance.entry.group_title,
                        })
        return context
