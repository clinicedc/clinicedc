class ModelAdminHideDeleteButtonOnCondition:
    def hide_delete_button_on_condition(self, request, object_id) -> bool:
        """Returns True if condition to hide button is met.

        Override.
        """
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Sets template context variable `show_delete` to False if
        `hide_delete_button_on_condition` returns True.
        """
        if self.hide_delete_button_on_condition(request, object_id):
            extra_context = extra_context or {}
            extra_context["show_delete"] = False
        elif extra_context:
            try:
                del extra_context["show_delete"]
            except KeyError:
                pass
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )
