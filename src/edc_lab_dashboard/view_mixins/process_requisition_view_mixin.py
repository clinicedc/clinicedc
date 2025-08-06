import re

from django.apps import apps as django_apps
from edc_constants.constants import UUID_PATTERN
from edc_lab.lab import Specimen as SpecimenObject
from edc_lab.site_labs import site_labs
from edc_label import LabPrintersMixin, add_job_results_to_messages


class ProcessRequisitionViewMixin(LabPrintersMixin):
    def process(self, request=None):
        """Creates aliquots according to the lab_profile.

        Actions handled by the Specimen object.
        """
        processed = {}
        for requisition in self.get_requisitions(
            pk__in=self.selected_items, received=True, processed=False
        ):
            specimen = SpecimenObject(requisition=requisition)
            if requisition.panel_object.processing_profile:
                processed.update({"requisition": specimen.process()})
                requisition.processed = True
                requisition.save()
        for created_aliquots in processed.values():
            pks = [specimen.primary_aliquot.pk] + [obj.pk for obj in created_aliquots]
            if pks:
                job_result = self.print_labels(pks=pks, request=request)
                if job_result:
                    add_job_results_to_messages(request, [job_result])

    @property
    def selected_items(self):
        """Returns a list of UUIDs as strings."""
        if not self._selected_items:
            for pk in self.request.POST.getlist(self.form_action_selected_items_name):
                if re.match(UUID_PATTERN, str(pk)):
                    self._selected_items.append(pk)
        return self._selected_items

    def get_requisitions(self, **kwargs):
        """Returns a list of requisition model instances filtered
        by the given kwargs.

        Searches all requisition model classes registered with
        site_labs.
        """
        requisitions = []
        for model in site_labs.requisition_models.values():
            model_cls = django_apps.get_model(model)
            requisitions.extend([r for r in model_cls.objects.filter(**kwargs)])
        return requisitions

    @property
    def processed_requisitions(self):
        """Returns a list of model instances that have been
        processed.
        """
        return self.get_requisitions(pk__in=self.selected_items, processed=True)

    @property
    def unprocessed_requisitions(self):
        """Returns a list of model instances that have NOT been
        processed.
        """
        return self.get_requisitions(pk__in=self.selected_items, processed=False)
