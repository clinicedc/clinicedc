import pytz

from arrow.arrow import Arrow
from django.apps import apps as django_apps
from django.conf import settings
from edc_label import Label
from edc_protocol import Protocol


class RequisitionLabel(Label):
    template_name = "requisition"
    registered_subject_model = "edc_registration.registeredsubject"

    def __init__(self, pk=None, requisition=None, item=None, **kwargs):
        super().__init__(label_template_name=self.template_name)
        self._registered_subject = None
        self.item = item or 1
        if requisition:
            self.requisition = requisition
        else:
            model, pk = pk
            self.requisition = django_apps.get_model(model).objects.get(pk=pk)
        self.label_name = self.requisition.human_readable_identifier

    @property
    def registered_subject(self):
        if not self._registered_subject:
            model_cls = django_apps.get_model(self.registered_subject_model)
            self._registered_subject = model_cls.objects.get(
                subject_identifier=self.requisition.subject_identifier
            )
        return self._registered_subject

    @property
    def label_context(self):
        tz = pytz.timezone(settings.TIME_ZONE)
        local = Arrow.fromdatetime(
            self.requisition.drawn_datetime or self.requisition.created
        ).to(tz)
        formatted_date = local.format("YYYY-MM-DD HH:mm")
        printed = "PRINTED: " if not self.requisition.drawn_datetime else "DRAWN: "
        drawn_datetime = f"{printed}{formatted_date}"
        try:
            clinician_initials = self.requisition.user_created[0:2].upper()
        except IndexError:
            clinician_initials = "??"
        return {
            "requisition_identifier": self.requisition.requisition_identifier,
            "item": self.item,
            "item_count": self.requisition.item_count or 1,
            "primary": "<P>",
            "barcode_value": self.requisition.requisition_identifier,
            "protocol": Protocol().protocol,
            "site": str(self.requisition.site.id),
            "site_name": str(self.requisition.site.name),
            "site_title": str(self.requisition.site.siteprofile.title),
            "clinician_initials": clinician_initials,
            "drawn_datetime": drawn_datetime,
            "subject_identifier": self.registered_subject.subject_identifier,
            "gender": self.registered_subject.gender,
            "dob": self.registered_subject.dob,
            "initials": self.registered_subject.initials,
            "identity": self.registered_subject.identity,
            "alpha_code": self.requisition.panel_object.alpha_code,
            "panel": self.requisition.panel_object.abbreviation,
            "panel_name": self.requisition.panel.display_name,
        }
