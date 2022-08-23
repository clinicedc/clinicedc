class TemplatesModelAdminMixin:
    """Override admin templates.

    Note: If using inlines.

    On the inline admin class specify the position `after` with class
    attribute `insert_after`:

    For example:
        class MyInlineModelAdmin(..):
            ...
            insert_after="<fieldname>"
            ...

    See also: https://linevi.ch/en/django-inline-in-fieldset.html
    """

    show_object_tools: bool = False

    add_form_template: str = "edc_model_admin/admin/change_form.html"
    change_form_template: str = "edc_model_admin/admin/change_form.html"
    change_list_template: str = "edc_model_admin/admin/change_list.html"
    view_on_site_label: str = "View on site"
    history_label: str = "Audit trail"
    delete_confirmation_template: str = "edc_model_admin/admin/delete_confirmation.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            {
                "view_on_site_label": self.view_on_site_label,
                "history_label": self.history_label,
            }
        )
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = {} if not extra_context else extra_context
        extra_context.update(
            {
                "show_object_tools": self.show_object_tools,
            }
        )
        return super().changelist_view(request, extra_context=extra_context)
