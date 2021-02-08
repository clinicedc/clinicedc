from django.db import transaction
from django.db.utils import IntegrityError


class SpecimenProcessorError(Exception):
    pass


class SpecimenProcessor:
    """A class to process a specimen into aliquots according
    to its processing profile.
    """

    def __init__(
        self,
        model_obj=None,
        processing_profile=None,
        identifier_prefix=None,
        aliquot_creator_cls=None,
    ):
        self.aliquot_creator_cls = aliquot_creator_cls
        self.model_obj = model_obj
        self.processing_profile = processing_profile
        self.identifier_prefix = identifier_prefix

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"processing_profile={self.processing_profile},"
            f"identifier_prefix={self.identifier_prefix})"
        )

    def create(self):
        """Creates all aliquots in the processing profile "processes"."""
        created = []
        count = 1
        for process in self.processing_profile.processes.values():
            aliquot_count = process.aliquot_count
            for _ in range(1, aliquot_count + 1):
                count += 1
                aliquot_creator = self.aliquot_creator_cls(
                    parent_identifier=self.model_obj.aliquot_identifier,
                    requisition_identifier=self.model_obj.requisition_identifier,
                    subject_identifier=self.model_obj.subject_identifier,
                    identifier_prefix=self.identifier_prefix,
                )
                with transaction.atomic():
                    try:
                        aliquot = aliquot_creator.create(
                            count=count, aliquot_type=process.aliquot_type
                        )
                    except IntegrityError:
                        pass
                    else:
                        created.append(aliquot)
        return created
