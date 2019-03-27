from django.db import models


class SubjectOnScheduleModelMixin(models.Model):

    """A model mixin to be added to a consent, crf or other model
    that when saved signifies a subject on schedule.

    Used when the "Onschedule" model is not a user model.
    This is NOT for the "Onschedule" model. See `OnScheduleModelMixin`.
    Triggers the "put on schedule" process.
    """

    def put_subject_on_schedule_on_post_save(self, created):
        """A wrapper to put a subject on schedule.

        Called in signals.
        """
        if created:
            self.schedule.put_on_schedule(
                subject_identifier=self.subject_identifier,
                onschedule_datetime=self.consent_datetime,
            )

    class Meta:
        abstract = True
