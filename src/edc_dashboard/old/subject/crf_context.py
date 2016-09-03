from edc_metadata.models import CrfMetaData

from .base_context import BaseContext


class CrfContext(BaseContext):

    """A Class used by the dashboard when rendering the
    list of scheduled entries to display under "Scheduled Forms"."""

    meta_data_model = CrfMetaData

    def contribute_to_context(self, context):
        context.update({'entry': self.meta_data_instance.crf_entry,
                        'entry_order': self.meta_data_instance.crf_entry.entry_order,
                        'group_title': self.meta_data_instance.crf_entry.group_title,
                        })
        return context
