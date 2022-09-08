from django.utils.html import format_html


class FormLabelModelAdminMixin:

    """A class that helps modify fieldsets for subject models

    * Model is expected to have a relation `subject_visit__appointment`.
    * Expects appointment to be in GET
    """

    custom_form_labels = []

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        return self.update_form_labels(request=request, obj=obj, form=form)

    def update_form_labels(self, request=None, obj=None, form=None):
        """Returns a form obj after modifying form labels
        referred to in custom_form_labels.
        """
        for form_label in self.custom_form_labels:
            if form_label.field in form.base_fields:
                label = form_label.get_form_label(
                    request=request, obj=obj, model=self.model, form=form
                )
                if label:
                    form.base_fields[form_label.field].label = format_html(label)
        return form
