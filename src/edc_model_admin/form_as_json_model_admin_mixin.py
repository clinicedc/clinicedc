class FormAsJSONModelAdminMixin:

    """Use with FormAsJSONModelformMixin, FormAsJSONModelMixin.
    """

    def save_model(self, request, obj, form, change):
        try:
            obj.form_as_json = form.as_json()
        except AttributeError:
            pass
        super().save_model(request, obj, form, change)
