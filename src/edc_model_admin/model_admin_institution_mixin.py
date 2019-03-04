from django.apps import apps as django_apps


class ModelAdminInstitutionMixin:

    """Adds institution attrs to the ModelAdmin context.
    """

    def get_institution_extra_context(self, extra_context):
        app_config = django_apps.get_app_config("edc_base")
        extra_context.update(
            {
                "institution": app_config.institution,
                "copyright": app_config.copyright,
                "license": app_config.license or "",
                "disclaimer": app_config.disclaimer,
            }
        )
        return extra_context

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context = self.get_institution_extra_context(extra_context)
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context = self.get_institution_extra_context(extra_context)
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )
