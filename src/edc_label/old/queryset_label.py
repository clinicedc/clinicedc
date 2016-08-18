from .model_label import ModelLabel


class QuerysetLabel(ModelLabel):
    """ Print a label building the template and context from the model."""

    def print_label(self, request, queryset):
        """Print a label for each model instance in the queryset."""
        for model_instance in queryset:
            super(QuerysetLabel, self).print_label(request, model_instance)
