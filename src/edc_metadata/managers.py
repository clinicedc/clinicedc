from django.db import models


class CrfMetadataManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(
        self,
        model,
        subject_identifier,
        schedule_name,
        visit_schedule_name,
        visit_code,
        visit_code_sequence,
    ):
        return self.get(
            model=model,
            subject_identifier=subject_identifier,
            schedule_name=schedule_name,
            visit_schedule_name=visit_schedule_name,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )


class RequisitionMetadataManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(
        self,
        panel_name,
        model,
        subject_identifier,
        visit_schedule_name,
        schedule_name,
        visit_code,
        visit_code_sequence,
    ):
        return self.get(
            panel_name=panel_name,
            model=model,
            subject_identifier=subject_identifier,
            schedule_name=schedule_name,
            visit_schedule_name=visit_schedule_name,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )
