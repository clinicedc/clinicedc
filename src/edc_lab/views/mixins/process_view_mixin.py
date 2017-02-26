from ...lab import Specimen


class ProcessViewMixin:

    def process(self):
        """Creates aliquots according to the lab_profile.

        Actions handled by the Specimen object.
        """
        created = []
        for requisition in self.requisition_model.objects.filter(
                pk__in=self.requisitions, received=True, processed=False):
            specimen = Specimen(requisition=requisition)
            if requisition.panel_object.processing_profile:
                created.extend(
                    specimen.primary_aliquot.create_aliquots_by_processing_profile(
                        processing_profile=requisition.panel_object.processing_profile))
                requisition.processed = True
                requisition.save()
