from ...lab import Specimen


class ProcessViewMixin:

    def process(self):
        """Creates aliquots according to the lab_profile.

        Actions handled by the Specimen object.
        """
        processed = {}
        for requisition in self.requisition_model.objects.filter(
                pk__in=self.requisitions, received=True, processed=False):
            specimen = Specimen(requisition=requisition)
            if requisition.panel_object.processing_profile:
                processed.update({
                    'requisition':
                    specimen.primary_aliquot.create_aliquots_by_processing_profile(
                        processing_profile=requisition.panel_object.processing_profile)})
                requisition.processed = True
                requisition.save()
        for created_aliquots in processed.values():
            self.print_labels(
                pks=[specimen.primary_aliquot] + [obj.pk for obj in created_aliquots])
