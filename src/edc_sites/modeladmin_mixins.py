from edc_sites.get_language_choices_for_site import get_language_choices_for_site


class SiteModelAdminMixin:
    """Adds the current site to the form from the request object.

    Use together with the `SiteModelFormMixin`.
    """

    language_db_field_name = "language"

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.currrent_site = getattr(request, "site", None)
        return form

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == self.language_db_field_name:
            try:
                language_choices = get_language_choices_for_site(request.site, other=True)
            except AttributeError as e:
                if "WSGIRequest" not in str(e):
                    raise
            else:
                if language_choices:
                    kwargs["choices"] = language_choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)
