from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import transaction


@receiver(post_save, weak=False, dispatch_uid="update_registered_subject_from_consent_on_post_save")
def update_registered_subject_from_consent_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates RegisteredSubject from the consent.

    Consent must have an AuditTrail manager (history), a FK to registered_subject
    and an 'identity' field."""
    if not raw and not kwargs.get('update_fields'):
        try:
            instance.history  # raise on models without an AuditTrail, e.g audit model classes
            with transaction.atomic():
                identity = instance.identity  # only a consent model has this field
                registered_subject = instance.registered_subject
                registered_subject.identity = identity
                registered_subject.last_name = instance.last_name
                registered_subject.first_name = instance.first_name
                registered_subject.identity_type = instance.identity_type
                registered_subject.subject_identifier = instance.subject_identifier
                registered_subject.registration_identifier = instance.pk
                registered_subject.dob = instance.dob
                registered_subject.is_dob_estimated = instance.is_dob_estimated
                registered_subject.gender = instance.gender
                registered_subject.initials = instance.initials
                registered_subject.study_site = instance.study_site
                registered_subject.save(using=using)
        except AttributeError as e:
            if '\'NoneType\' object has no attribute \'pk\'' in str(e):
                pass
            elif ('registered_subject' not in str(e) and
                  'identity' not in str(e) and
                  'history' not in str(e) and 'last_name' not in str(e)):
                raise AttributeError(str(e))
