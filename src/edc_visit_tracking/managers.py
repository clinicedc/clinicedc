from django.db import models


class CrfModelManager(models.Manager):
    """A manager class for Crf models, models that have an FK to
    the visit model.
    """

    def get_by_natural_key(self, subject_identifier, visit_schedule_name,
                           schedule_name, visit_code, visit_code_sequence):
        instance = self.model.visit_model_cls().objects.get_by_natural_key(
            subject_identifier, visit_schedule_name, schedule_name,
            visit_code, visit_code_sequence)
        return self.get(**{self.model.visit_model_attr(): instance})

    def get_for_visit(self, visit, **kwargs):
        """Returns an instance for the given visit.
        """
        options = {self.model.visit_model_attr(): visit}
        options.update(**kwargs)
        return self.get(**options)

    def filter_for_visit(self, visit, **kwargs):
        """Returns an instance for the given visit.
        """
        options = {self.model.visit_model_attr(): visit}
        options.update(**kwargs)
        return self.filter(**options)

    def get_for_subject_identifier(self, subject_identifier):
        """Returns a queryset for the given subject_identifier.
        """
        options = {'{}__subject_identifier'.format(
            self.model.visit_model_attr()): subject_identifier}
        return self.filter(**options)


class VisitModelManager(models.Manager):
    """A manager class for visit models.
    """

    def get_by_natural_key(self, subject_identifier, visit_schedule_name,
                           schedule_name, visit_code, visit_code_sequence):
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence)

    def last_visit(self, subject_identifier=None, visit_schedule_names=None,
                   schedule_names=None):
        """Returns the last visit for a subject.

        By specify visit_schedule_name and/or schedule_name,
        the last visit becomes the last visit for within the visit schedule
        or schedule.

        Note: schedule names are in
        <visit_schedule_name>.<schedule_name> dot format
        """
        options = {}
        if schedule_names:
            schedule_names = [name.split('.')[-1] for name in schedule_names]
            if not visit_schedule_names and '.' in schedule_names[0]:
                visit_schedule_names = list(
                    set([name.split('.')[0] for name in schedule_names]))
        if subject_identifier:
            options.update(dict(subject_identifier=subject_identifier))
        if visit_schedule_names:
            options.update(dict(visit_schedule_name__in=visit_schedule_names))
        return self.filter(**options).order_by('report_datetime').last()
