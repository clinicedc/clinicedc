from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_protocol import Protocol

from ..site_labs import site_labs
from .base_label import BaseLabel


class AliquotLabelError(Exception):
    pass


class AliquotLabel(BaseLabel):
    model = "edc_lab.aliquot"
    template_name = "aliquot"
    registered_subject_model = "edc_registration.registeredsubject"

    def __init__(self, pk=None, children_count=None, request=None):
        super().__init__(pk=pk, request=request)
        self._registered_subject = None
        self._requisition = None
        self.children_count = children_count

    @property
    def requisition(self):
        """Returns a requisition model instance for this
        requisition_identifier."""
        if not self._requisition:
            for model in site_labs.requisition_models:
                model_cls = django_apps.get_model(model)
                try:
                    self._requisition = model_cls.objects.get(
                        requisition_identifier=self.model_obj.requisition_identifier
                    )
                except ObjectDoesNotExist:
                    pass
                else:
                    break
            if not self._requisition:
                raise AliquotLabelError(
                    "Requisition does not exist. "
                    f"requisition_identifier={self.model_obj.requisition_identifier}. "
                    f"Tried models {site_labs.requisition_models}"
                )
        return self._requisition

    @property
    def label_context(self):
        registered_subject = django_apps.get_model(self.registered_subject_model).objects.get(
            subject_identifier=self.requisition.subject_identifier
        )
        return {
            "aliquot_identifier": self.model_obj.human_readable_identifier,
            "aliquot_count": 1 if self.model_obj.is_primary else self.model_obj.count,
            "children_count": 1 if self.model_obj.is_primary else self.children_count,
            "primary": "<P>" if self.model_obj.is_primary else "",
            "barcode_value": self.model_obj.aliquot_identifier,
            "protocol": Protocol().protocol,
            "site": str(self.requisition.site.id),
            "site_name": str(self.requisition.site.name),
            "site_title": str(self.requisition.site.siteprofile.title),
            "clinician_initials": self.requisition.user_created[0:2].upper(),
            "drawn_datetime": self.requisition.drawn_datetime.strftime("%Y-%m-%d %H:%M"),
            "subject_identifier": registered_subject.subject_identifier,
            "gender": registered_subject.gender,
            "dob": registered_subject.dob.strftime("%Y-%m-%d"),
            "initials": registered_subject.initials,
            "alpha_code": self.model_obj.alpha_code,
            "panel": self.requisition.panel_object.abbreviation,
            "panel_name": self.requisition.panel.display_name,
        }
