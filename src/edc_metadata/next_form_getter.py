from .constants import REQUIRED
from .metadata import CrfMetadataGetter, RequisitionMetadataGetter


class NextFormGetter:

    crf_metadata_getter_cls = CrfMetadataGetter
    requisition_metadata_getter_cls = RequisitionMetadataGetter

    def next_form(self, model_obj=None, appointment=None, model=None, panel_name=None):
        """Returns the next required form based on the metadata.

        A form is a Crf or Requisition object from edc_visit_schedule.
        """
        next_form = None

        if model_obj:
            appointment = model_obj.visit.appointment
            model = model_obj._meta.label_lower
            visit = model_obj.visit.visit
            try:
                panel_name = model_obj.panel.name
            except AttributeError:
                panel_name = None
        else:
            visit = appointment.visit.visit
            panel_name = panel_name

        if panel_name:
            this_form = visit.get_requisition(
                model=model, panel_name=panel_name)
            getter = self.requisition_metadata_getter_cls(
                appointment=appointment)
            default_next_form = None
        else:
            this_form = visit.get_crf(model=model)
            getter = self.crf_metadata_getter_cls(
                appointment=appointment)
            default_next_form = self.first_requisition_form(
                appointment=appointment, visit=visit)

        metadata_obj = getter.next_object(
            show_order=this_form.show_order, entry_status=REQUIRED)

        if metadata_obj:
            if panel_name:
                next_form = visit.get_requisition(
                    metadata_obj.model, panel_name=metadata_obj.panel_name)
            else:
                next_form = visit.get_crf(metadata_obj.model)
        return next_form or default_next_form

    def first_requisition_form(self, appointment=None, visit=None):
        first_requisition_form = None
        metadata_getter_cls = self.requisition_metadata_getter_cls
        getter = metadata_getter_cls(appointment=appointment)
        metadata_obj = getter.next_object(show_order=0, entry_status=REQUIRED)
        if metadata_obj:
            first_requisition_form = visit.get_requisition(
                metadata_obj.model, panel_name=metadata_obj.panel_name)
        return first_requisition_form
