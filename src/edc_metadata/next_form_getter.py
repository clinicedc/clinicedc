from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .constants import REQUIRED
from .metadata import CrfMetadataGetter, RequisitionMetadataGetter

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_visit_schedule import Crf, Requisition, Visit

    from .metadata import MetadataGetter
    from .models import CrfMetadata, RequisitionMetadata


class NextFormGetter:
    crf_metadata_getter_cls = CrfMetadataGetter
    requisition_metadata_getter_cls = RequisitionMetadataGetter

    def __init__(
        self,
        model_obj=None,
        appointment: Appointment = None,
        model: str = None,
        panel_name: str = None,
    ):
        self._getter = None
        self._next_metadata_obj = None
        self._model_obj = model_obj
        self._next_form = None
        self._next_panel = None
        self._panel_name = panel_name

        self.model = model or model_obj._meta.label_lower
        self.appointment = appointment or model_obj.related_visit.appointment
        self.visit: Visit = self.appointment.related_visit.visit

    @property
    def next_form(self) -> Crf | Requisition:
        """Returns the next required form based on the metadata.

        A form is a Crf or Requisition object from edc_visit_schedule.
        """
        if not self._next_form:
            next_model = getattr(self.next_metadata_obj, "model", None)
            self._next_form = self.visit.get_requisition(
                next_model, panel_name=self.next_panel
            ) or self.visit.get_crf(next_model)
        return self._next_form

    @property
    def model_obj(self):
        """Returns the model instance of the current CRF or
        Requisition.
        """
        if not self._model_obj:
            model_cls = django_apps.get_model(self.model)
            try:
                self._model_obj = model_cls.objects.get(
                    **{
                        f"{model_cls.related_visit_model_attr()}__appointment": (
                            self.appointment
                        )
                    }
                )
            except ObjectDoesNotExist:
                pass
        return self._model_obj

    @property
    def metadata_getter(self) -> MetadataGetter | RequisitionMetadataGetter:
        """Returns a metadata_getter instance."""
        if not self._getter:
            if self.panel_name:
                self._getter = self.requisition_metadata_getter_cls(
                    appointment=self.appointment
                )
            else:
                self._getter = self.crf_metadata_getter_cls(appointment=self.appointment)
        return self._getter

    @property
    def next_metadata_obj(self) -> CrfMetadata | RequisitionMetadata:
        """Returns the "next" metadata model instance or None."""
        if not self._next_metadata_obj:
            show_order = getattr(self.crf_or_requisition, "show_order", None)
            self._next_metadata_obj = self.metadata_getter.next_object(
                show_order=show_order, entry_status=REQUIRED
            )
        return self._next_metadata_obj

    @property
    def next_panel(self) -> str | None:
        if not self._next_panel:
            if self.next_metadata_obj:
                try:
                    self._next_panel = self.next_metadata_obj.panel_name
                except AttributeError:
                    pass
        return self._next_panel

    @property
    def panel_name(self) -> str | None:
        """Returns a panel_name or None."""
        if not self._panel_name:
            if self.model_obj:
                try:
                    self._panel_name = self.model_obj.panel.name
                except AttributeError:
                    self._panel_name = None
        return self._panel_name

    @property
    def crf_or_requisition(self) -> Crf | Requisition:
        """Returns a CRF or Requisition object from
        the visit schedule's visit.
        """
        crf = None
        requisition = None
        if self.panel_name:
            requisition = self.visit.get_requisition(
                model=self.model, panel_name=self.panel_name
            )
        else:
            crf = self.visit.get_crf(model=self.model)
        return crf or requisition
