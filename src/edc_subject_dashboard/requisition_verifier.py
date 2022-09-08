from django.core.exceptions import ObjectDoesNotExist
from edc_appointment.models import Appointment
from edc_constants.constants import NO, YES
from edc_lab.constants import TUBE
from edc_lab.model_mixins import RequisitionModelMixin
from edc_utils import get_utcnow


class RequisitionVerifier:

    """Update a requisition's "verify" fields.

    Also sets defaults for any other fields that are required
    if pre-print a label.
    """

    def __init__(self, appointment_pk=None, requisition_identifier=None):
        self._requisition = None
        self.verified = None
        self.appointment = Appointment.objects.get(pk=appointment_pk)
        self.requisition_identifier = requisition_identifier
        if self.requisition and self.requisition.is_drawn != NO:
            # verification fields
            self.requisition.clinic_verified = YES
            self.requisition.clinic_verified_datetime = get_utcnow()
            # other fields for label printing
            self.requisition.is_drawn = self.requisition.is_drawn or YES
            self.requisition.item_count = self.requisition.item_count or 1
            self.requisition.item_type = self.requisition.item_type or TUBE
            self.requisition.drawn_datetime = self.requisition.drawn_datetime or get_utcnow()
            self.requisition.save()
            self.verified = self.requisition.clinic_verified

    def __str__(self):
        return f"{self.requisition_identifier} {self.verified}"

    def __repr__(self):
        return f"<{self.__class__.__name__}(" "{self.requisition_identifier}) {self.verified}>"

    @property
    def requisition(self):
        """Returns a requisition model instance."""
        if not self._requisition:
            try:
                self._requisition = self.requisition_model_cls.objects.get(
                    requisition_identifier=self.requisition_identifier.strip()
                )
            except ObjectDoesNotExist:
                pass
        return self._requisition

    @property
    def requisition_model_cls(self):
        """Returns the requisition model class.

        Discovers the requisition model class from the visit
        model.
        """
        model_cls = None
        visit_model_cls = self.appointment.related_visit.__class__
        for attr in dir(visit_model_cls):
            try:
                obj = getattr(getattr(visit_model_cls, attr), "rel")
            except AttributeError:
                pass
            else:
                try:
                    model_cls = obj.related_model
                except AttributeError:
                    pass
                else:
                    if issubclass(model_cls, (RequisitionModelMixin,)):
                        break
        return model_cls
