from edc_lab.lab import Specimen as SpecimenObject
from edc_label import add_job_results_to_messages


class ProcessViewMixin:

    def process(self, request=None):
        """Creates aliquots according to the lab_profile.

        Actions handled by the Specimen object.
        """
        processed = {}
        job_results = []
        for requisition in self.requisition_model.objects.filter(
                pk__in=self.requisitions, received=True, processed=False):
            specimen = SpecimenObject(requisition=requisition)
            if requisition.panel_object.processing_profile:
                processed.update({'requisition': specimen.process()})
                requisition.processed = True
                requisition.save()
        for created_aliquots in processed.values():
            job_results.extend(self.print_labels(
                pks=([specimen.primary_aliquot.pk]
                     + [obj.pk for obj in created_aliquots]),
                request=request))
        add_job_results_to_messages(request, job_results)
