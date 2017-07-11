from django.db.utils import IntegrityError
from django.db import transaction


class SpecimenProcessorError(Exception):
    pass


class SpecimenProcessor:
    """A class to process a specimen according to its processing
    profile.
    """

    def __init__(self, model_obj=None, processing_profile=None,
                 aliquot_creator_cls=None, aliquot_identifier_cls=None,
                 identifier_length=None, identifier_prefix=None,
                 count_padding=None, **kwargs):
        self.object = model_obj
        self.aliquot_creator_cls = aliquot_creator_cls
        self.aliquot_identifier_cls = aliquot_identifier_cls
        self.processing_profile = processing_profile

        self.aliquot_creator_defaults = dict(
            aliquot_model=model_obj.__class__,
            count_padding=count_padding,
            identifier_length=identifier_length,
            identifier_prefix=identifier_prefix,
        )

    def create(self):
        """Creates all aliquots in the porcessing profile.
        """
        created = []
        count = 1
        for process in self.processing_profile.processes.values():
            aliquot_count = process.aliquot_count
            for _ in range(1, aliquot_count + 1):
                count += 1
                with transaction.atomic():
                    try:
                        aliquot_creator = self.aliquot_creator_cls(
                            aliquot_identifier_cls=self.aliquot_identifier_cls,
                            parent_identifier=self.object.aliquot_identifier,
                            requisition_identifier=self.object.requisition_identifier,
                            subject_identifier=self.object.subject_identifier,
                            **self.aliquot_creator_defaults
                        )
                        aliquot = aliquot_creator.create(
                            count=count, aliquot_type=process.aliquot_type)
                    except IntegrityError:
                        # raise SpecimenProcessorError(e) from e
                        pass
                    else:
                        created.append(aliquot)
        return created
