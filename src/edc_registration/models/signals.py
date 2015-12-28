from django.db.models.signals import post_save
from django.dispatch import receiver

from edc_constants.constants import CONSENTED


@receiver(post_save, weak=False, dispatch_uid="consent_on_post_save")
def consent_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates RegisteredSubject on consent."""
    if not raw:
        try:
            registered_subject = instance.registered_subject
            registered_subject.identity = instance.identity
            instance.registered_subject.last_name = instance.last_name
            registered_subject.first_name = instance.first_name
            registered_subject.identity_type = instance.identity_type
            registered_subject.subject_identifier = instance.subject_identifier
            registered_subject.registration_datetime = instance.consent_datetime
            registered_subject.registration_status = CONSENTED
            registered_subject.registration_identifier = instance.pk
            registered_subject.dob = instance.dob
            registered_subject.is_dob_estimated = instance.is_dob_estimated
            registered_subject.gender = instance.gender
            registered_subject.initials = instance.initials
            registered_subject.study_site = instance.study_site
            registered_subject.save(using=using)
            print('hello4')
        except AttributeError as e:
            if 'registered_subject' not in str(e) and 'identity' not in str(e):
                raise AttributeError(str(e))
