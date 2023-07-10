inline_hide_object_original_name = True


class InlineHideOriginalObjectNameMixin:

    """Declare with main ModelAdmin class, not the InlineModelAdmin class.

    Only works if declared with the TabularInlineMixin.
    """

    inline_hide_object_original_name = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.insert_before_fieldset = self.insert_before_fieldset
        return formset

    def add_view(self, request, form_url: str = "", extra_context: dict = None):
        extra_context = extra_context or {}
        extra_context.update(
            inline_hide_object_original_name=self.inline_hide_object_original_name
        )
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            inline_hide_object_original_name=self.inline_hide_object_original_name
        )
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )
