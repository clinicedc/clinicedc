from edc_lab.lab import Specimen as SpecimenObject


class ProcessViewMixin:

    def process(self):
        """Creates aliquots according to the lab_profile.

        Actions handled by the Specimen object.
        """
        processed = {}
        for requisition in self.requisition_model.objects.filter(
                pk__in=self.requisitions, received=True, processed=False):
            specimen = SpecimenObject(requisition=requisition)
            if requisition.panel_object.processing_profile:
                processed.update({'requisition': specimen.process()})
                requisition.processed = True
                requisition.save()
        for created_aliquots in processed.values():
            self.print_labels(
                pks=[specimen.primary_aliquot.object.pk] + [obj.pk for obj in created_aliquots])
