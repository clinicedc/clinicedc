class TemplatesModelAdminMixin:

    show_object_tools = False

    add_form_template = "edc_model_admin/admin/change_form.html"
    change_form_template = "edc_model_admin/admin/change_form.html"
    change_list_template = "edc_model_admin/admin/change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = {} if not extra_context else extra_context
        extra_context.update({"show_object_tools": self.show_object_tools})
        return super().changelist_view(request, extra_context=extra_context)
