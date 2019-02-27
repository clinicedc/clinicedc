from django.apps import apps as django_apps


class AliquotLabelMixin:
    @property
    def requisition(self):
        model = django_apps.get_model(*self.receive.requisition_model_name)
        return model.objects.get(
            requisition_identifier=self.receive.requisition_identifier
        )

    def label_context(self, extra_context=None):
        label_context = {}
        primary = ""
        if self.aliquot_identifier[-2:] == "01":
            primary = "<"
        label_context.update(
            {
                "aliquot_count": self.aliquot_count,
                "aliquot_identifier": self.aliquot_identifier,
                "aliquot_type": self.aliquot_type.name,
                "clinician_initials": self.requisition.clinician_initials,
                "drawn_datetime": self.requisition.drawn_datetime,
                "primary": primary,
                "site": str(self.requisition.site.id),
            }
        )
        if extra_context:
            label_context.update(extra_context)
        return label_context
