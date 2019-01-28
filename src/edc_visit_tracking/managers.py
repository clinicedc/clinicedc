from django.db import models


class CrfModelManager(models.Manager):
    """A manager class for Crf models, models that have an FK to
    the visit model.
    """

    use_in_migrations = True

    def get_by_natural_key(
        self,
        subject_identifier,
        visit_schedule_name,
        schedule_name,
        visit_code,
        visit_code_sequence,
    ):
        instance = self.model.visit_model_cls().objects.get_by_natural_key(
            subject_identifier,
            visit_schedule_name,
            schedule_name,
            visit_code,
            visit_code_sequence,
        )
        return self.get(**{self.model.visit_model_attr(): instance})


class VisitModelManager(models.Manager):
    """A manager class for visit models.
    """

    def get_by_natural_key(
        self,
        subject_identifier,
        visit_schedule_name,
        schedule_name,
        visit_code,
        visit_code_sequence,
    ):
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )
