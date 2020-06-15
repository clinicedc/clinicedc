from edc_protocol import Protocol


class ModelAdminInstitutionMixin:
    """Adds institution attrs to the ModelAdmin context.
    """

    @staticmethod
    def get_institution_extra_context(extra_context):
        protocol = Protocol()
        extra_context.update(
            {
                "institution": protocol.institution,
                "copyright": protocol.copyright,
                "license": protocol.license or "",
                "disclaimer": protocol.disclaimer,
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
